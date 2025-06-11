from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from flaskr.models import Base    
from flaskr.db import db

class Server(db.Model):
    __tablename__ = "servers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    banner_url = db.Column(db.String(255))  # np. obrazek z bannerem serwera
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacje
    votes = relationship("Vote", back_populates="server", cascade="all, delete-orphan")
    skins = relationship("Skin", back_populates="server", cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="servers")