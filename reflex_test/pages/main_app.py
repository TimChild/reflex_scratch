"""The dashboard page."""

from ..components.google_auth import require_google_login, AuthState
from ..styles import submit_button_style
from reflex_test.templates import template

import reflex as rx


class TextState(rx.State):
    value: str = ""
    submitted_value: str = ""

    def handle_submit(self):
        self.submitted_value = self.value


class TokenInfo(rx.Base):
    iss: str
    azp: str
    aud: str
    sub: str
    email: str
    email_verified: bool
    name: str
    picture: str
    given_name: str
    family_name: str
    iat: int
    exp: int
    jti: str


class UserState(rx.State):
    user: str = "Guest"
    token_info: TokenInfo = None

    async def init_auth(self):
        auth_state = await self.get_state(AuthState)
        self.token_info = auth_state.tokeninfo

    @rx.var
    def info(self) -> str:
        if not self.token_info:
            return "No token info"
        items = []
        for key, value in self.token_info.items():
            items.append(f"{key}: {value}")
        s = "\n\r".join(items)
        return f"Token info: {s}"


@template(route="/", title="Scratch", description="Main app")
@require_google_login
def main_app() -> rx.Component:
    """"""
    return rx.container(
        rx.vstack(
            rx.form(
                rx.text_area(
                    width="100%",
                    placeholder="How can I...",
                    auto_height=True,
                    rows="5",
                    on_change=TextState.set_value,
                    on_blur=lambda e: TextState.handle_submit(),
                    enter_key_submit=True,
                ),
                width="100%",
                on_submit=lambda e: TextState.handle_submit(),
            ),
            rx.text_area(
                read_only=True,
                value=TextState.submitted_value,
                width="100%",
                auto_height=True,
            ),
            rx.button(
                "Submit",
                style=submit_button_style,
                on_click=TextState.handle_submit,
            ),
            rx.divider(),
            rx.text("Debugging info:"),
            # rx.text_area(value=UserState.info, read_only=True, width='100%'),
            rx.text_area(value=UserState.info, width="100%", is_read_only=True),
            # rx.text(f'Current user: {UserState.user}'),
            rx.button("Login", on_click=UserState.init_auth),
        ),
    )
