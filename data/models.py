from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Base class for all models."""
    pass

class User(Base):
    """The Owner (User #1)."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    recovery_key: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    timezone: Mapped[str] = mapped_column(String(32), default="UTC")

class Activity(Base):
    """Time tracking logs."""
    __tablename__ = "activities"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Context
    mood: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_flow: Mapped[bool] = mapped_column(Boolean, default=False)
    power_source: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    ate_breakfast: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

class Spending(Base):
    """Financial logs."""
    __tablename__ = "spending"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(64))
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    payment_method: Mapped[Optional[str]] = mapped_column(String(64), default="PalmPay")

class Pattern(Base):
    """Learned behaviors (The Fingerprint)."""
    __tablename__ = "patterns"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(128), index=True)
    value: Mapped[str] = mapped_column(String(2048))  # JSON or simple string
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
