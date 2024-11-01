from typing import Optional
from pydantic import BaseModel, EmailStr, constr, field_validator
from app.utils.validators import validate_name


ALLOWED_NAME_REGEX = r"^[a-zA-Z0-9\-_.,()\[\]{}@#&]*$"


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator("first_name", "last_name")
    def validate_name_field(cls, name):
        return validate_name(name)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]

    class Config:
        from_attributes = True

