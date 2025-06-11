from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

from .user import User
from .server import Server
from .vote import Vote
from .skin import Skin  # jeśli też chcesz go testować

__all__ = ['User', 'Server', 'Vote', 'Skin']