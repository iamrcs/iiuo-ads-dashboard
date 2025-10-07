from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine, func
import datetime
import os

Base = declarative_base()

# Database file (SQLite for easy Koyeb deploy)
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./iiuo_ads.db")

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# -----------------------------
# User Model
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    websites = relationship("Website", back_populates="owner")


# -----------------------------
# Website Model
# -----------------------------
class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    verification_token = Column(String, unique=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="websites")

    ad_events = relationship("AdEvent", back_populates="website")


# -----------------------------
# Ad Events (Clicks & Impressions)
# -----------------------------
class AdEvent(Base):
    __tablename__ = "ad_events"

    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"))
    event_type = Column(String)  # 'impression' or 'click'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    website = relationship("Website", back_populates="ad_events")


# -----------------------------
# Revenue Calculation Helper
# -----------------------------
def calculate_revenue(impressions: int, clicks: int) -> float:
    # Simple estimated revenue model
    # e.g., 0.002 per impression + 0.05 per click
    return round(impressions * 0.002 + clicks * 0.05, 2)


# -----------------------------
# Database Init
# -----------------------------
def init_db():
    Base.metadata.create_all(bind=engine)
