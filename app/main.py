from fastapi import FastAPI, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from . import models, auth, schemas, track, verify
import secrets

# -----------------------------
# App Initialization
# -----------------------------
app = FastAPI(title="IIUO Ads Dashboard")
app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))

models.init_db()  # Create DB tables

templates = Jinja2Templates(directory="app/templates")

# Dependency
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Include Routers
# -----------------------------
app.include_router(track.router, prefix="/api")
app.include_router(verify.router, prefix="/api")

# -----------------------------
# Home Page
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -----------------------------
# Register
# -----------------------------
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered."}
        )

    user = models.User(
        email=email,
        password_hash=auth.hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

# -----------------------------
# Login
# -----------------------------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials."}
        )

    token = auth.create_access_token({"user_id": user.id})
    response = RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

# -----------------------------
# Dashboard
# -----------------------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/login")

    user = auth.decode_access_token(token)
    db_user = db.query(models.User).filter(models.User.id == user["user_id"]).first()
    if not db_user:
        return RedirectResponse("/login")

    websites_stats = []
    for site in db_user.websites:
        impressions = db.query(models.AdEvent).filter(
            models.AdEvent.website_id == site.id,
            models.AdEvent.event_type == "impression"
        ).count()

        clicks = db.query(models.AdEvent).filter(
            models.AdEvent.website_id == site.id,
            models.AdEvent.event_type == "click"
        ).count()

        revenue = models.calculate_revenue(impressions, clicks)

        websites_stats.append({
            "id": site.id,
            "name": site.name,
            "domain": site.domain,
            "verified": site.is_verified,
            "verification_token": site.verification_token,
            "impressions": impressions,
            "clicks": clicks,
            "revenue": revenue
        })

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": db_user, "websites": websites_stats}
    )

# -----------------------------
# Add Website
# -----------------------------
@app.post("/add-website")
def add_website(
    request: Request,
    name: str = Form(...),
    domain: str = Form(...),
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/login")

    user_data = auth.decode_access_token(token)
    user = db.query(models.User).filter(models.User.id == user_data["user_id"]).first()
    if not user:
        return RedirectResponse("/login")

    # Generate verification token
    verification_token = secrets.token_urlsafe(16)

    website = models.Website(
        name=name,
        domain=domain,
        verification_token=verification_token,
        owner_id=user.id
    )
    db.add(website)
    db.commit()
    db.refresh(website)

    return RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)

# -----------------------------
# Logout
# -----------------------------
@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
