"""REST API views for authentication and account utilities."""

from __future__ import annotations

import base64
from io import BytesIO
from typing import Dict

import pyotp
import qrcode
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer

User = get_user_model()


def _issue_tokens(user: User) -> Dict[str, str]:
    """Return a dict containing refresh and access JWT tokens for ``user``."""

    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Create a new user account."""

    username = (request.data.get("username") or "").strip()
    email = (request.data.get("email") or "").strip()
    password = request.data.get("password") or ""
    role = (request.data.get("role") or "owner").lower()

    if not username or not email or not password:
        return Response(
            {"error": "Username, email, and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if role not in {choice[0] for choice in User.ROLE_CHOICES}:
        return Response(
            {"error": "Role must be one of: owner, accountant."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role=role,
    )

    serialized = UserSerializer(user)
    return Response(serialized.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """Authenticate a user and return JWT tokens."""

    username = request.data.get("username")
    password = request.data.get("password")
    token = (request.data.get("token") or "").strip()

    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

    if user.two_factor_secret:
        if not token:
            return Response(
                {"error": "Two-factor token is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(token, valid_window=1):
            return Response({"error": "Invalid 2FA token."}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(_issue_tokens(user), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    """Return profile information for the authenticated user."""

    serialized = UserSerializer(request.user)
    data = serialized.data
    data.pop("two_factor_secret", None)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generate_2fa(request):
    """Generate or return an existing 2FA secret for the authenticated user."""

    user: User = request.user

    if not user.two_factor_secret:
        user.two_factor_secret = pyotp.random_base32()
        user.save(update_fields=["two_factor_secret"])

    totp = pyotp.TOTP(user.two_factor_secret)
    otp_uri = totp.provisioning_uri(name=user.email or user.username, issuer_name="Pretium Investment")

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(otp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return Response(
        {
            "otp_uri": otp_uri,
            "qr_code_base64": img_base64,
        }
    )
