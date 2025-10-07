import secrets
import requests
from .models import Site
from sqlalchemy.orm import Session

# -----------------------------
# Token Generation
# -----------------------------
def generate_verification_token(length=32):
    """
    Generate a secure random token for site verification.
    """
    return secrets.token_urlsafe(length)

# -----------------------------
# Create or Get Site
# -----------------------------
def create_site(db: Session, user_id: int, name: str, domain: str):
    """
    Create a new site for a user with a verification token.
    If the site already exists, return it.
    """
    site = db.query(Site).filter(Site.user_id == user_id, Site.domain == domain).first()
    if site:
        return site

    token = generate_verification_token()
    new_site = Site(
        user_id=user_id,
        name=name,
        domain=domain,
        verification_token=token,
        verified=False,
        impressions=0,
        clicks=0
    )
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    return new_site

# -----------------------------
# Verify Site Ownership
# -----------------------------
def verify_site(db: Session, site: Site) -> bool:
    """
    Check the site's /ads.txt for the verification token.
    If token exists, mark site as verified.
    """
    try:
        url = f"https://{site.domain}/ads.txt"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200 and site.verification_token in resp.text:
            site.verified = True
            db.commit()
            return True
    except requests.RequestException:
        return False
    return False

# -----------------------------
# Verify All User Sites
# -----------------------------
def verify_user_sites(db: Session, user_id: int):
    """
    Verify all sites for a user. Returns a dict of domain -> status.
    """
    sites = db.query(Site).filter(Site.user_id == user_id).all()
    result = {}
    for site in sites:
        result[site.domain] = verify_site(db, site)
    return result
