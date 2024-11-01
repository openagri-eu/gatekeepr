from fastapi import APIRouter
from app.handlers.auth_handlers import login_page, validate_login, verify_user, create_user, validate_tokens_route

router = APIRouter(prefix="/auth", tags=["auth"])
router.add_api_route("/login", login_page, methods=["GET"])
router.add_api_route("/validate_login", validate_login, methods=["POST"])
router.add_api_route("/validate_tokens", validate_tokens_route, methods=["POST"])
router.add_api_route("/verify", verify_user, methods=["GET"])
router.add_api_route("/create_user", create_user, methods=["POST"])
