import reflex as rx

from reflex_test.templates import template


class Comp(rx.ComponentState):
    value: int = 0

    @classmethod
    def get_component(cls, v, *children, **props) -> rx.Component:
        return rx.card(
            rx.text(f"This one works > {v}"),  # <<< This alone works
            # rx.text(f"This one does not > {cls.value}"),  # <<< Adding this causes error
        )


@template(route="/component_state_in_foreach_issue", title="Component State in Foreach Issue")
def index() -> rx.Component:
    return rx.container(
        # rx.foreach(
        #     [1, 2, 3],
        #     Comp.create,
        # ),
        rx.text("Patched in 0.5.0 to raise an error at compile if trying to use Component.create in a foreach loop."),
    )
