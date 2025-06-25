from flaskr.db import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id        = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(50),  unique=True, nullable=False)
    email     = db.Column(db.String(100), unique=True, nullable=False)
    password  = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(256), unique=True, nullable=True)

    servers = relationship(
        "Server",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    votes = relationship(
        "Vote",
        back_populates="voter",
        cascade="all, delete-orphan"
    )