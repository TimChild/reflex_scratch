"""Reflex chatroom -- send server events to other sessions."""

import time
import typing as t

from reflex.state import BaseState

import reflex as rx

from reflex_test.templates import template


class Message(rx.Base):
    username: str
    sent: float
    message: str


class ChatroomState(rx.State):
    current_username: t.Optional[str] = ""
    all_usernames: t.List[str] = []
    messages: t.List[Message] = []
    input_message: str = ""

    def set_usernames(self, usernames: t.List[str]) -> None:
        """Set the list of usernames (from broadcast_usernames)."""
        print(f"Usernames: {usernames}")
        self.all_usernames = usernames

    def incoming_message(self, message: Message) -> None:
        """Append incoming message to current message list."""
        self.messages.append(message)

    async def username_change(self, username: str) -> None:
        """Handle on_blur from username text input."""
        self.current_username = username
        await broadcast_usernames()

    async def send_message(self) -> None:
        """Broadcast chat message to other connected clients."""
        m = Message(username=self.current_username, sent=time.time(), message=self.input_message)
        await broadcast_event("state.chatroom_state.incoming_message", payload=dict(message=m))
        self.input_message = ""

    @rx.var
    def other_usernames(self) -> t.List[str]:
        """Filter all_usernames list to exclude username from this instance."""
        return [n for n in self.all_usernames if n != self.current_username]


@template(
    route="/chatroom",
    title="Test Chatroom",
    description="Chatroom",
)
def chatroom() -> rx.Component:
    return rx.vstack(
        rx.center(rx.heading("Reflex Chat!", font_size="2em")),
        rx.hstack(
            rx.vstack(
                rx.input(
                    placeholder="Username",
                    default_value=ChatroomState.current_username,
                    on_blur=ChatroomState.username_change,
                ),
                rx.text("Other Users", font_weight="bold"),
                rx.foreach(ChatroomState.other_usernames, rx.text),
                width="20vw",
                align_items="left",
            ),
            rx.vstack(
                rx.foreach(
                    ChatroomState.messages,
                    lambda m: rx.text("<", m.username, "> ", m.message),
                ),
                rx.form(
                    rx.hstack(
                        rx.input(
                            placeholder="Message",
                            value=ChatroomState.input_message,
                            on_change=ChatroomState.set_input_message,
                            flex_grow=1,
                        ),
                        rx.button("Send", on_click=ChatroomState.send_message),
                    ),
                    on_submit=lambda d: ChatroomState.send_message(),
                ),
                width="60vw",
                align_items="left",
            ),
        ),
    )


async def broadcast_event(name: str, payload: t.Dict[str, t.Any] = {}) -> None:
    """Simulate frontend event with given name and payload from all clients."""
    from reflex_test.reflex_test import app

    responses = []
    for state in app.state_manager.states.values():
        state: BaseState
        async for update in state._process(
            event=rx.event.Event(
                token=state.router.session.client_token,
                name=name,
                router_data=state.router_data,
                payload=payload,
            ),
        ):
            # Emit the event.
            responses.append(
                app.event_namespace.emit(
                    str(rx.constants.SocketEvent.EVENT),
                    update.json(),
                    to=state.router.session.session_id,
                ),
            )
    for response in responses:
        await response


async def broadcast_usernames() -> None:
    """Simulate State.set_usernames event with updated username list from all clients."""
    from reflex_test.reflex_test import app

    usernames = []
    for state in app.state_manager.states.values():
        usernames.append(state.get_substate(ChatroomState.get_full_name().split(".")).current_username)
    await broadcast_event("state.chatroom_state.set_usernames", payload=dict(usernames=usernames))
