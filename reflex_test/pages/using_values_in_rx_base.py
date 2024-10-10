import logging
import reflex as rx

from reflex_test.templates import template

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SomeBase(rx.Base):
    a: int = 0
    b: int = 0
    c: int = 0


class ValsState(rx.State):
    base: SomeBase = SomeBase()

    @rx.var(cached=True)
    def a_plus_b(self) -> int:
        return self.base.a + self.base.b

    def increment_a(self):
        self.base.a += 1

    def increment_b(self):
        self.base.b += 1

    def increment_c(self):
        self.base.c += 1


@template(route="/using_values_in_rxBase", title="Using values in rxBase")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Using values in rxBase", size="5"),
            rx.divider(),
            rx.text(f"Value of a: {ValsState.base.a}"),
            rx.text(f"Value of b: {ValsState.base.b}"),
            rx.text(f"Value of c: {ValsState.base.c}"),
            rx.hstack(
                rx.button("Increment a", on_click=ValsState.increment_a),
                rx.button("Increment b", on_click=ValsState.increment_b),
                rx.button("Increment c", on_click=ValsState.increment_c),
            ),
            rx.divider(),
            rx.text(f"Value of a + b: {ValsState.a_plus_b}"),
            rx.divider(),
        ),
        padding="2em",
    )
