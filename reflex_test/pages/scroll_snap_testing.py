import reflex as rx

from reflex.components.radix.themes.components.scroll_area import ScrollArea

from ..templates import template

# Relevant css
"""
.scroll-area-test {
    border: #0BC5EA 1px solid;
        scroll-snap-type: y mandatory;

}

.scroll-item-test {
    scroll-snap-align: start;
}
"""


class ExtendedScrollArea(ScrollArea):
    # Allowed values are: ['none', 'x', 'y', 'block', 'inline', 'both', 'mandatory', 'proximity']
    # including combinations like 'x mandatory', 'y proximity'
    scroll_snap_type: rx.Var[str] = "none"
    pass


extended_scroll_area = ExtendedScrollArea.create


def scroll_test_layout() -> rx.Component:
    item = rx.card(
        rx.heading("Scroll test", size="3"),
        rx.text("This is a test of the scroll area"),
        height="20em",
        class_name="scroll-item-test",
    )
    return extended_scroll_area(*[item] * 10, class_name="scroll-area-test", scroll_snap_type="mandatory")


@template(route="/scroll_snap", title="Scroll Snap Testing", description="Testing scroll snap")
def index() -> rx.Component:
    return scroll_test_layout()
