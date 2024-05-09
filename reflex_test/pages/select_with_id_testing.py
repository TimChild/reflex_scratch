import random
import reflex as rx

from ..templates import template

choices = ["a", "b", "c", "d", "e", "f", "g"]


class SelectValueState(rx.State):
    selected_value: str = "a"

    def set_random_value_by_state_var(self):
        self.selected_value = random.choice(choices)

    def set_values_by_rx_event(self):
        yield rx.set_value("select-id", random.choice(choices))
        yield rx.set_value("another-select-id", random.choice(choices))
        yield rx.set_value("input-id", random.choice(choices))


@template(route="/select_with_id", title="Select with ID testing")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.select(
                    choices,
                    value=SelectValueState.selected_value,
                    on_change=SelectValueState.set_selected_value,
                    id="select-id",
                ),
                rx.text(f"Selected value is: {SelectValueState.selected_value}"),
            ),
            rx.hstack(
                rx.select(choices, id="another-select-id"),
                rx.text("Only expecting to see the value change in the select itself"),
            ),
            rx.hstack(
                rx.button("Set random value by state var", on_click=SelectValueState.set_random_value_by_state_var),
                rx.button(
                    "Set random value with rx.set_value",
                    on_click=[
                        SelectValueState.set_values_by_rx_event,
                    ],
                ),
            ),
            rx.hstack(
                rx.text("Showing that the rx.set_value works for an rx.input"),
                rx.input(id="input-id"),
            ),
        ),
    )
