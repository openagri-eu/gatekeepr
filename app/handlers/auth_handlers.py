# Only for route-related operations.

from fastapi import Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.config.settings import settings
from app.dependencies import get_db
from app.services.auth_service import (create_user_service, authenticate_user_service, verify_user_service,
                                       validate_tokens)
from app.schemas import UserCreate


# Configure templates directory
templates = Jinja2Templates(directory="templates")


async def login_page(request: Request):
    next_url = request.query_params.get("next", "/")
    error = request.query_params.get("error")
    return templates.TemplateResponse("login.html", {"request": request, "next": next_url, "error": error})


async def validate_login(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/")
):
    user, access_token, refresh_token = authenticate_user_service(db, username, password)
    if user:
        # Determine the redirect URL based on the `next` parameter using redirects.json data
        redirect_url = None
        for keyword, url in settings.redirects.items():
            if keyword.lower() in next.lower():
                redirect_url = url
                break

        redirect_url = redirect_url or settings.redirects.get("default", "/")

        redirect_url_with_tokens = f"{redirect_url}?access_token={access_token}&refresh_token={refresh_token}"

        return JSONResponse({
            "success": True,
            "redirect_url": redirect_url_with_tokens
        })

        # Return JSON response with redirect URL and set both tokens as cookies
        # response = JSONResponse({"success": True, "redirect_url": redirect_url})
        # response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax")
        # response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax")
        # return response

    error_message = "Invalid credentials"
    return JSONResponse({"success": False, "error": error_message})


async def register_page(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse("register.html", {"request": request, "error": error})


async def register_user(
        request: Request,
        db: Session = Depends(get_db),
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
):
    user_data = UserCreate(username=username, email=email, password=password)

    try:
        # Call create_user_service to create a new user
        create_user_service(db, user_data)
        # Redirect to login page upon successful registration
        return RedirectResponse(url="/auth/login", status_code=303)

    except HTTPException as e:
        # Redirect back to register page with error message if registration fails
        return templates.TemplateResponse("register.html", {"request": request, "error": e.detail})


async def validate_tokens_route(request: Request,
                                access_token: Optional[str] = Form(None),
                                refresh_token: Optional[str] = Form(None)):
    if not access_token:
        access_token = request.cookies.get("access_token")
    if not refresh_token:
        refresh_token = request.cookies.get("refresh_token")

    return await validate_tokens(access_token=access_token, refresh_token=refresh_token)


async def verify_user(token: str = Depends(verify_user_service)):
    return {"message": f"Verified user: {token['username']}"}


async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return create_user_service(db, user_data)


async def test_route():
    return {"message": "Test route"}
