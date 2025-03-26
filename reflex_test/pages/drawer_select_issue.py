import reflex as rx
from reflex_test.templates import template


@template(route="/drawer_select_issue", title="Drawer select issue")
# @rx.page(route="/drawer_select_issue", title="Select not working in drawer")
def index() -> rx.Component:
    return rx.container(
        rx.text(
            "2025-03-26 -- Was having issue with rx.select inside a rx.drawer... The select dropdown would immediately close when opened. This ended up being fixed by setting the select position to 'popper' instead of the default 'item-aligned'."
        ),
        rx.color_mode.button(),
        rx.popover.root(
            rx.popover.trigger(rx.button("Open Popover")),
            rx.popover.content(
                rx.select(["a", "b", "c"]),
                rx.popover.close(rx.button("Close")),
            ),
        ),
        rx.drawer.root(
            rx.drawer.trigger(rx.button("Open Drawer")),
            rx.drawer.overlay(z_index="5"),
            rx.drawer.portal(
                rx.drawer.content(
                    rx.hstack(
                        rx.drawer.close(rx.box(rx.button("Close"))),
                        rx.select(["d", "e", "f"], position="popper"),
                        # background="unset",
                    ),
                    background=rx.color("gray", 2),
                    width="20em",
                ),
            ),
            # handle_only=True,
            direction="bottom",
        ),
    )
