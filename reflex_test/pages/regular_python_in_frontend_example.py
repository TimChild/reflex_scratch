import reflex as rx

from reflex_test.templates import template


def button_maker(label: str, type: str) -> rx.Component:
    if type == "basic":
        return rx.button(label)
    elif type == "fancy":
        return rx.button(rx.text(label, color="gold"), variant="outline", color_scheme="plum")
    else:
        raise NotImplementedError


@template(
    route="/example",
    title="Example",
)
def index() -> rx.Component:
    return rx.container(
        rx.center(
            rx.vstack(
                rx.heading('Regular python in otherwise "frontend" code', size="3"),
                button_maker("Basic Button", "basic"),
                button_maker("Fancy Button", "fancy"),
                align="center",
            ),
            height="100vh",
        ),
    )
