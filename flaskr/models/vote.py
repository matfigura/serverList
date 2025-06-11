from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from flaskr.models import Base
from flaskr.db import db

class Vote(db.Model):
    __tablename__ = "votes"

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, ForeignKey("servers.id"), nullable=False)
    voter_ip = db.Column(db.String(45), nullable=False)  # IPv6 safe
    voted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, ForeignKey("users.id"), nullable=True)  # <--- dodane
    voter = relationship("User", back_populates="votes")  

    server = relationship("Server", back_populates="votes")