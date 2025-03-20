import reflex as rx
from reflex_test.templates import template


@template(route="/drawer_select_issue", title="Select not working in drawer")
# @rx.page(route="/drawer_select_issue", title="Select not working in drawer")
def index() -> rx.Component:
    return rx.container(
        rx.drawer.root(
            rx.drawer.trigger(rx.button("Open Drawer")),
            rx.drawer.overlay(z_index="5"),
            rx.drawer.portal(
                rx.drawer.content(
                    rx.flex(
                        rx.drawer.close(rx.box(rx.button("Close"))),
                        rx.select(["a", "b", "c"]),
                    ),
                    background_color="#FFF",
                    width="20em",
                ),
            ),
            direction="left",
        ),
    )
