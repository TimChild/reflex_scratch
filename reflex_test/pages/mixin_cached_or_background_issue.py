import logging
import reflex as rx

from reflex_test.templates import template

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class BasicMixin(rx.State, mixin=True):
    a: int = 0
    b: int = 0
    c: int = 0

    @rx.var
    def var_a(self) -> int:
        logger.debug("var_a called")
        return self.a + 10

    @rx.cached_var
    def cached_a(self) -> int:
        logger.debug("cached_a called")
        return self.a + 20

    def increment_a(self):
        self.a += 1

    async def increment_b(self):
        self.b += 1

    @rx.background
    async def increment_c(self):
        async with self:
            self.c += 1


class StateWithBasicMixin(BasicMixin, rx.State):
    pass


@template(route="/mixin_cached_or_background_issue", title="Mixin Cached or Background Issue")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Mixin Cached or Background Issue", size="5"),
            rx.grid(
                rx.text("Attr a:"),
                rx.text(StateWithBasicMixin.a),
                rx.text("Var a:"),
                rx.text(StateWithBasicMixin.var_a),
                rx.text("Cached a:"),
                rx.text(StateWithBasicMixin.cached_a),
                rx.text("Attr b:"),
                rx.text(StateWithBasicMixin.b),
                rx.text("Attr c:"),
                rx.text(StateWithBasicMixin.c),
                columns="5",
                rows="2",
                flow="column",
            ),
            rx.hstack(
                rx.button("Increment a", on_click=StateWithBasicMixin.increment_a),
                rx.button("Increment b", on_click=StateWithBasicMixin.increment_b),
                rx.button("Increment c", on_click=StateWithBasicMixin.increment_c),
            ),
        ),
        padding="2em",
    )
