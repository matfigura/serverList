from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from flaskr.models import Base 
from flaskr.db import db

class Skin(db.Model):
    __tablename__ = "skins"

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, ForeignKey("servers.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    server = relationship("Server", back_populates="skins")