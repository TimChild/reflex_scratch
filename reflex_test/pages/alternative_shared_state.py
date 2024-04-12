"""
https://github.com/reflex-dev/reflex/issues/1857


2024-04-10 -- I think this might have some information in that would improve the updating of shared states...
Specifically the `async with app.modify_state(token)` part.
Maybe even possible to set the whole state with `app.state_manager.set_state(...)`?
"""

import reflex as rx

from ..reflex_test import app
from ..templates import template

# Keep track of tokens associated with the same client browser ("shared" sessions)
shared_sessions_by_token: dict[str, set[str]] = {}

# Keep track of (shared_token, state_token) pairs for each websocket connection (sid)
tokens_by_sid: dict[str, tuple[str, str]] = {}


class State(rx.State):
    # The clientToken is saved in the browser and identifies "shared" sessions
    clientToken: str = rx.Cookie("")

    # The colorState is a special variable that is shared among all sessions with the same clientToken
    colorState: str = "green"

    def ChangePage1Color(self):
        self.colorState = "red"

        # Apply changes to all other shared sessions
        return State.set_color_state_for_shared_sessions

    def ChangePage2Color(self):
        self.colorState = "yellow"

        # Apply changes to all other shared sessions
        return State.set_color_state_for_shared_sessions

    async def set_color_state_for_shared_sessions(self):
        """Iterate through all shared sessions and update them with the new colorState."""
        if not self.clientToken:
            self.set_client_token()

        print(f"{self.clientToken} -> {shared_sessions_by_token[self.clientToken]}")

        for token in shared_sessions_by_token.get(self.clientToken, set()):
            if token != self.get_token():
                async with app.modify_state(token) as other_state:
                    other_state.colorState = self.colorState

    async def set_color_state_for_new_session(self):
        """When a new session is created, copy the colorState from another shared session."""
        for token in shared_sessions_by_token.get(self.clientToken, set()):
            if token != self.get_token():
                async with app.modify_state(token) as other_state:
                    self.colorState = other_state.colorState

                    # app.state_manager.set_state(token, other_state)  # <<< Can this be used?
                    return

    def set_client_token(self):
        """Page on_load handler uses the clientToken cookie to identify shared sessions."""
        if not self.clientToken:
            self.clientToken = self.get_token()

        # Mark this state's token as belonging to the clientToken
        shared_sessions_by_token.setdefault(self.clientToken, set()).add(
            self.get_token()
        )

        # Mark this state's websocket id as belonging to the clientToken and state token
        tokens_by_sid[self.get_sid()] = (self.clientToken, self.get_token())

        # Set the colorState for the new session from existing shared sessions (if any)
        return State.set_color_state_for_new_session


@template("/alternative_shared_state_1", title="Alternative Shared State 1")
def page1() -> rx.Component:
    return rx.vstack(
        rx.button(
            "Click 1",
            on_click=State.ChangePage1Color,
        ),
        rx.box(
            rx.text(
                State.colorState,
            ),
            background_color=State.colorState,
        ),
    )


@template("/alternative_shared_state_2", title="Alternative Shared State 2")
def page2() -> rx.Component:
    return rx.vstack(
        rx.button(
            "Click 2",
            on_click=State.ChangePage2Color,
        ),
        rx.box(
            rx.text(
                State.colorState,
            ),
            background_color=State.colorState,
        ),
    )


# Handle websocket disconnect events to avoid memory leaks when sessions are closed
orig_disconnect = app.event_namespace.on_disconnect


def disconnect_handler(sid):
    orig_disconnect(sid)

    clientToken, token = tokens_by_sid.get(sid, (None, None))
    print(
        f"Disconnect event received for {sid}. Removing {token} from shared {clientToken}"
    )

    shared_sessions_by_token.get(clientToken, set()).discard(token)
    tokens_by_sid.pop(sid, None)


app.event_namespace.on_disconnect = disconnect_handler
