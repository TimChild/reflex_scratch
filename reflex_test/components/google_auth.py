import os
import functools
import json
import time

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token

import reflex as rx

from .react_oauth_google import GoogleOAuthProvider, GoogleLogin

from dotenv import load_dotenv  # noqa: F401

CLIENT_ID = os.environ.get(
    "GOOGLE_CLIENT_ID",
    "587721936400-dc0in5bvrkadoas6d9ottl1e8vf3qlsm.apps.googleusercontent.com",
)
print(f"Found client id={CLIENT_ID}")
# CLIENT_ID = ''


class AuthState(rx.State):
    id_token_json: str = rx.LocalStorage()

    def on_success(self, id_token: dict):
        self.id_token_json = json.dumps(id_token)

    @rx.var(cache=True)
    def tokeninfo(self) -> dict[str, str]:
        try:
            return verify_oauth2_token(
                json.loads(self.id_token_json)["credential"],
                requests.Request(),
                CLIENT_ID,
                clock_skew_in_seconds=5,
            )
        except Exception as exc:
            if self.id_token_json:
                print(f"Error verifying token: {exc}")
        return {}

    def logout(self):
        self.id_token_json = ""

    @rx.var
    def token_is_valid(self) -> bool:
        try:
            return bool(self.tokeninfo and int(self.tokeninfo.get("exp", 0)) > time.time())
        except Exception:
            return False

    @rx.var(cache=True)
    def protected_content(self) -> str:
        if self.token_is_valid:
            return f"This content can only be viewed by a logged in User. Nice to see you {self.tokeninfo['name']}"
        return "Not logged in."


def user_info(tokeninfo: dict) -> rx.Component:
    return rx.hstack(
        rx.avatar(
            name=tokeninfo["name"],
            src=tokeninfo["picture"],
            size="9",
        ),
        rx.vstack(
            rx.heading(tokeninfo["name"], size="6"),
            rx.text(tokeninfo["email"]),
            align_items="flex-start",
        ),
        rx.button("Logout", on_click=AuthState.logout),
        padding="10px",
    )


def login() -> rx.Component:
    return rx.vstack(
        GoogleLogin.create(on_success=AuthState.on_success),
    )


def require_google_login(page) -> rx.Component:
    @functools.wraps(page)
    def _auth_wrapper() -> rx.Component:
        return GoogleOAuthProvider.create(
            rx.cond(
                AuthState.is_hydrated,
                rx.cond(AuthState.token_is_valid, page(), login()),
                rx.spinner(),
            ),
            client_id=CLIENT_ID,
        )

    return _auth_wrapper


def index():
    return rx.vstack(
        rx.heading("Google OAuth", size="9"),
        rx.link("Protected Page", href="/protected"),
    )
