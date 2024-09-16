import reflex as rx
from reflex.constants.colors import ColorType
import lorem

from reflex_test.templates import template

COLORS = [
    "pink",
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
    "grass",
]

component_map = {
    "code": lambda text: rx.code(text, color="purple", max_width="100%"),
    # "codeblock": lambda text, **props: rx.code_block(
    #     text, **props, margin_y="1em", max_width="100%", wrap_long_lines=True, can_copy=False, theme="dark"
    # ),
    # "codeblock": lambda text, **props: rx.scroll_area(rx.code_block(
    #     text, **props, margin_y="1em", max_width="100%", wrap_long_lines=True, can_copy=False, theme="dark"
    # ), max_heigh="500px", max_width="100%", theme="dark"),
    "codeblock": lambda text, **props: rx.code_block(
        text, **props, margin_y="1em", max_width="100%", wrap_long_lines=True, can_copy=False, theme="dark", show_line_numbers=True
    ),
}


def _md_contents() -> rx.Component:
    return rx.markdown(
        f"`inline code`\n\n```python\ndef foo():\n    return 'bar'\n{
            lorem.sentence()}\n```\n\n{lorem.paragraph()}",
        display="inline-block",
        border_radius="10px",
        max_width="100%",
        component_map=component_map
    )


def render_box(color: ColorType, index: int) -> rx.Component:
    # print(color)
    return rx.box(
        # rx.text(f"Box {index}: {lorem.paragraph()}"),
        _md_contents(),
        background_color=rx.color(color=color),
        width="100%",
        # height="100px",
        height="fit-content",
    )


def _scroll_contents() -> rx.Component:
    return rx.vstack(*[
        render_box(c, i)
        for i, c in enumerate(COLORS)
    ]
    )


def _simple_scroll_area() -> rx.Component:
    return rx.scroll_area(
        _scroll_contents(),
        height="300px",
        type="hover",
        max_width="100%",
        scrollbars="vertical",
    )


def _scroll_area_in_container() -> rx.Component:
    return rx.container(
        _simple_scroll_area(),
        size="1",
        max_width="100%",
    )


def scroll_area_in_box_only(scroll_area) -> rx.Component:
    return rx.box(
        rx.heading("Scrollarea directly in box"),
        scroll_area,
        width="100%",
        border="1px solid blue",
    )


def scroll_area_in_container(scroll_area) -> rx.Component:
    return rx.box(
        rx.heading(
            "Scroll area additionally in a container"
        ),
        rx.container(
            scroll_area,
            size="1",
            max_width="100%",
        ),
        width="100%",
        border="1px solid red",
    )


def good_scroll_area() -> rx.Component:
    return rx.box(
        rx.heading("This box demonstrates a solution"),
        rx.vstack(
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
                height="300px",
                scrollbars="vertical",
                overflow_x="hidden",
            ),
            height="100%",
        ),
        name="box-area",
        width="100%",
        align="center",
        border="1px solid green",
    )


@rx.page(route="/scroll_area_width_issue", title="Scroll Area Width Issue")
def index() -> rx.Component:
    s1 = _simple_scroll_area()
    s2 = _scroll_area_in_container()

    return rx.vstack(
        rx.heading(
            "Problem where the rx.scroll_area width is not constrained to the parent box width."),
        rx.text(
            "Seem to have trouble restricting the width of elements that are inside of an rx.scroll_area... This page tries to isolate that issue and present a solution."
        ),
        scroll_area_in_box_only(s2),
        scroll_area_in_container(s2),

        scroll_area_in_box_only(s1),
        scroll_area_in_container(s1),
        # good_scroll_area(),
    )
