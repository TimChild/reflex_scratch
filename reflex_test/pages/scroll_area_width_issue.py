import reflex as rx
from reflex.constants.colors import ColorType

from reflex_test.templates import template

COLORS = ["pink",
          "plum",
          "purple",
          "violet",
          "iris",
          "indigo",
          "blue",
          "cyan",
          "teal",
          "jade",
          "green",
          "grass", ]


def render_box(color: ColorType, index: int) -> rx.Component:
    # print(color)
    return rx.box(
        rx.text(f"Box {index}"),
        background_color=rx.color(color=color),
        width="90%",
        height="100px",
    )


def scroll_area_part() -> rx.Component:
    return rx.box(
        rx.scroll_area(
            rx.container(
                rx.vstack(
                    *[render_box(c, i) for i, c in enumerate(COLORS)],
                    width="100%",
                ),
                padding_top="1em",
                size="4",
            ),
            type="hover",
            width="100%",
            height='300px',
            scrollbars="vertical",
            overflow_x="hidden",
        ),
        width="100%",
        overflow_y="hidden",
    )


@template(route="/scroll_area_width_issue", title="Scroll Area Width Issue")
def index() -> rx.Component:
    return rx.box(
        rx.fragment(
            rx.vstack(
                rx.heading("Problem where the rx.scroll_area width is not constrained to the parent box width."),
                scroll_area_part(),
                height="100%",
            )),

        name='box-area',
        width="100%",
        align="center",
        border="1px solid green",
    )
