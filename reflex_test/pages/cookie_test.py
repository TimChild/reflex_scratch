import reflex as rx
from reflex_test.templates import template


class State(rx.State):
    cookie_a: str = rx.Cookie(name="cookie_a")

    @rx.event
    def update(self, data: dict[str, str]) -> None:
        self.cookie_a = data["new_value"]


@template("/cookie_test", title="Cookie Test")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.text("Cookie value:"),
            rx.text(State.cookie_a),
            rx.form(
                rx.input(
                    name="new_value",
                    placeholder="new cookie value",
                ),
                rx.button("update"),
                on_submit=State.update,
            ),
        )
    )
