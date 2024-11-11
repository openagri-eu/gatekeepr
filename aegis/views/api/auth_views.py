# views/api_views.py

import requests

from django import forms
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from datetime import datetime

from aegis.forms import UserRegistrationForm
from aegis.services.auth_services import register_user, authenticate_user


@method_decorator(never_cache, name='dispatch')
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user, access_token, refresh_token = authenticate_user(username, password)

        if user:
            return Response({
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "error": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(never_cache, name='dispatch')
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        form = UserRegistrationForm(request.data)

        if form.is_valid():
            try:
                register_user(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"]
                )
                return Response({
                    "success": True,
                    "message": "User registered successfully. Please log in."
                }, status=status.HTTP_201_CREATED)

            except forms.ValidationError as e:
                return Response({
                    "success": False,
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # Return validation errors
        return Response({
            "success": False,
            "errors": form.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(never_cache, name='dispatch')
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"success": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


class TokenValidationAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        token_type = request.data.get("token_type", "access")
        token = request.data.get("token")

        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is an access or refresh token
        try:
            if token_type == "access":
                token_instance = AccessToken(token)
            elif token_type == "refresh":
                token_instance = RefreshToken(token)
            else:
                return Response({"error": "Invalid token type. Must be 'access' or 'refresh'."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Get expiration time
            expiration_time = token_instance["exp"]

        except Exception:
            return Response({"error": f"Invalid or expired {token_type} token"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Calculate remaining time (in seconds)
        current_time = datetime.utcnow()
        remaining_time = expiration_time - current_time.timestamp()

        if remaining_time > 0:
            return Response({
                "success": True,
                "remaining_time_in_seconds": remaining_time
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Token has already expired"
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def reverse_proxy(request, path):

    provider_api = None
    for open_agri_entity, resource_provider_id in settings.REVERSE_PROXY_MAPPING.items():
        if open_agri_entity in path:
            provider_api = settings.AVAILABLE_SERVICES.get(resource_provider_id, {}).get('api')
    if provider_api is None:
        return JsonResponse({'error': 'No service can provide this resource.'}, status=405)

    url = f"{provider_api}{path}"
    method = request.method

    # Forward the request headers and body
    headers = {key: value for key, value in request.headers.items() if key != 'Host'}
    data = request.body

    # Forward the request based on the HTTP method
    if method == 'POST':
        response = requests.post(url, headers=headers, data=data)
    elif method == 'GET':
        response = requests.get(url, headers=headers, params=request.GET)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, data=data)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers, data=data)
    else:
        return JsonResponse({'error': 'Method not supported'}, status=405)

    # Create a Django response object with the same status code and content
    return HttpResponse(
        response.content,
        status=response.status_code,
        content_type=response.headers.get('Content-Type', 'application/json')
    )