import reflex as rx

from reflex_test.templates import template


class Mixin1(rx.State, mixin=True):
    value1: int = 0


class Mixin2(rx.State, mixin=True):
    value2: int = 2


class SubclassMixin1(Mixin1, mixin=True):
    sub_value1: int = 1


class CombinedState(SubclassMixin1, Mixin2, rx.State):
    value3: int = 3

    def update_values(self):
        self.value1 += 1
        self.sub_value1 += 2
        self.value2 += 1
        self.value3 += 1


@template(route="/inherit_multiple_mixin", title="Inherit Multiple Mixin")
def index() -> rx.Component:
    return rx.container(
        rx.heading("Inherit Multiple Mixin", size="5"),
        rx.text("Trying out inheriting from multiple mixins that subclass `rx.State` with `mixin=True`."),
        rx.text(f"The value of `value1` is {CombinedState.value1}"),
        rx.text(f"The value of `sub_value1` is {CombinedState.sub_value1}"),
        rx.text(f"The value of `value2` is {CombinedState.value2}"),
        rx.text(f"The value of `value3` is {CombinedState.value3}"),
        rx.button("Update values", on_click=CombinedState.update_values),
        rx.divider(),
        rx.text(
            "Any mixin should be defined with super class `rx.State` and `mixin=True`. Additionally, any subclass"
            "of a mixin should also include `mixin=True`, and then the final class should inherit from any mixins "
            "plus `rx.State` without specifying `mixin = True`"
        ),
    )
