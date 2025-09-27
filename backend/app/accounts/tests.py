"""API integration tests for the accounts app."""

from __future__ import annotations

import base64

import pyotp
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationTests(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.profile_url = reverse("profile")
        self.generate_2fa_url = reverse("generate-2fa")
        self.password = "StrongPass123!"

    def test_user_can_register_and_login_without_2fa(self) -> None:
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": self.password,
        }
        register_response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        login_response = self.client.post(
            self.login_url,
            {"username": payload["username"], "password": self.password},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

    def test_login_requires_two_factor_token_when_enabled(self) -> None:
        user = get_user_model().objects.create_user(
            username="bob",
            email="bob@example.com",
            password=self.password,
            role="owner",
        )
        user.two_factor_secret = pyotp.random_base32()
        user.save(update_fields=["two_factor_secret"])

        missing_token = self.client.post(
            self.login_url,
            {"username": "bob", "password": self.password},
            format="json",
        )
        self.assertEqual(missing_token.status_code, status.HTTP_401_UNAUTHORIZED)

        totp = pyotp.TOTP(user.two_factor_secret)
        with_token = self.client.post(
            self.login_url,
            {
                "username": "bob",
                "password": self.password,
                "token": totp.now(),
            },
            format="json",
        )
        self.assertEqual(with_token.status_code, status.HTTP_200_OK)
        self.assertIn("access", with_token.data)

    def test_generate_2fa_returns_otpauth_uri_and_qr_code(self) -> None:
        user = get_user_model().objects.create_user(
            username="carol",
            email="carol@example.com",
            password=self.password,
            role="owner",
        )

        login_response = self.client.post(
            self.login_url,
            {"username": "carol", "password": self.password},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.generate_2fa_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("otp_uri", response.data)
        self.assertIn("qr_code_base64", response.data)
        # Ensure the QR code is a valid base64 string.
        base64.b64decode(response.data["qr_code_base64"], validate=True)
