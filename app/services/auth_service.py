from fastapi import HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional

from app.auth.auth_utils import hash_password, verify_password, create_jwt_token, decode_jwt_token
from app.models.user import User
from app.schemas import UserCreate


def create_user_service(db: Session, user_data: UserCreate):
    if db.query(User).filter(or_(User.username == user_data.username, User.email == user_data.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed_password = hash_password(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}


def authenticate_user_service(db: Session, login: str, password: str):
    # Query for user by username or email
    user = db.query(User).filter(or_(User.username == login, User.email == login)).first()

    # Verify password
    if not user or not verify_password(password, user.password):
        return None, None, None

    # Generate both access and refresh tokens
    token_data = {"user_id": user.id, "username": user.username, "email": user.email}
    access_token = create_jwt_token(token_data, token_type="access")
    refresh_token = create_jwt_token(token_data, token_type="refresh")

    return user, access_token, refresh_token


def verify_user_service(token: str = Depends(decode_jwt_token)):
    return token  # Returns decoded token details for verification


# Service to validate tokens (access and/or refresh)
async def validate_tokens(access_token: Optional[str] = None, refresh_token: Optional[str] = None):
    # Case 1: Only access token provided
    if access_token and not refresh_token:
        try:
            decode_jwt_token(access_token)
            return JSONResponse({"valid": True, "message": "Access token is valid."})
        except HTTPException as e:
            return JSONResponse({"valid": False, "message": e.detail}, status_code=401)

    # Case 2: Only refresh token provided
    elif refresh_token and not access_token:
        try:
            decode_jwt_token(refresh_token)
            return JSONResponse({"valid": True, "message": "Refresh token is valid."})
        except HTTPException as e:
            return JSONResponse({"valid": False, "message": e.detail}, status_code=401)

    # Case 3: Both tokens provided
    elif access_token and refresh_token:
        try:
            decode_jwt_token(access_token)
            return JSONResponse({"valid": True, "message": "Access token is valid."})

        except HTTPException as access_exception:
            if access_exception.detail == "Token expired":
                try:
                    payload = decode_jwt_token(refresh_token)
                    token_data = {"user_id": payload["user_id"], "username": payload["username"],
                                  "email": payload["email"]}
                    new_access_token = create_jwt_token(token_data, token_type="access")

                    response = JSONResponse({
                        "valid": True,
                        "message": "New access token generated.",
                        "access_token": new_access_token
                    })
                    response.set_cookie(key="access_token", value=new_access_token, httponly=True, samesite="lax")
                    return response

                except HTTPException as refresh_exception:
                    return JSONResponse({
                        "valid": False,
                        "message": "Both access and refresh tokens are expired. Please log in again."
                    }, status_code=401)

            return JSONResponse({"valid": False, "message": access_exception.detail}, status_code=401)

    # Case 4: No tokens provided
    else:
        return JSONResponse({"valid": False, "message": "No tokens provided."}, status_code=400)
