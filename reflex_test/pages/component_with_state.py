import reflex as rx

from reflex_test.templates import template

from ..components import component_with_state


@template(
    route="/component_with_state",
    title="Component with State",
)
def index() -> rx.Component:
    return rx.container(
        rx.heading("Component with State page:"),
        component_with_state(
            rx.text("Child 1"),
            rx.text("Child 2"),
            rx.text("Child 3"),
        ),
    )
