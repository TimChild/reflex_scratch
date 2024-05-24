import reflex as rx

from reflex_test.templates import template


class Mixin1(rx.State, mixin=True):
    value1: int = 0


class Mixin2(rx.State, mixin=True):
    value2: int = 2


class CombinedState(Mixin1, Mixin2, rx.State):
    value3: int = 3


@template(route="/inherit_multiple_mixin", title="Inherit Multiple Mixin")
def index() -> rx.Component:
    return rx.container(
        rx.heading("Inherit Multiple Mixin", size="5"),
        rx.text("Trying out inheriting from multiple mixins that subclass `rx.State` with `mixin=True`."),
        rx.text(f"The value of `value1` is {CombinedState.value1}"),
        rx.text(f"The value of `value2` is {CombinedState.value2}"),
        rx.text(f"The value of `value3` is {CombinedState.value3}"),
    )
