from flask_sqlalchemy import SQLAlchemy
from webapp.models.user import User
from webapp.models.society import Society

db = SQLAlchemy()

# def init():
#     """init
#     """
#     db.create_all()

__all__ = [
    User, Society
]