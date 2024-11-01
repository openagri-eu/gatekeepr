from sqlalchemy import Column, String
from sqlalchemy.orm import validates

from app.models.base import BaseModel
from app.utils.validators import *


class User(BaseModel):
    __tablename__ = "user_master"

    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

    @validates("email")
    def validate_email(self, key, email):
        return validate_email(email)

    @validates("username")
    def validate_username(self, key, username):
        return validate_username(username)

    @validates("password")
    def validate_password(self, key, password):
        return validate_password(password)

    @validates("first_name", "last_name")
    def validate_name_fields(self, key, name):
        return validate_name(name)