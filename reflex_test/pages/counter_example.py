from typing import ClassVar
import reflex as rx

from reflex_test.templates.template import template


class Counter(rx.ComponentState):
    # Define vars that change.
    count: int = 0

    # Be careful about this being a mutable object.
    on_increment_listener: ClassVar[list[rx.EventHandler]] = None

    # Define event handlers.
    def increment(self) -> list[rx.EventHandler]:
        self.count += 1
        return self.on_increment_listener

    def decrement(self):
        self.count -= 1

    @classmethod
    def get_component(cls, **props):
        # Access the state vars and event handlers using `cls`.
        return rx.hstack(
            rx.button("Decrement", on_click=cls.decrement,
                      id="button-decrement"),
            rx.text(cls.count, id="counter-value"),
            rx.button("Increment", on_click=cls.increment,
                      id="button-increment"),
            **props,
        )

    @classmethod
    def register_listener(cls, event_handler: rx.EventHandler) -> None:
        if cls.on_increment_listener is None:
            cls.on_increment_listener = [event_handler]
        else:
            cls.on_increment_listener.append(event_handler)


class OtherState(rx.State):
    value: int = 0

    def increment_when_counter_increments(self):
        self.value += 2


@template(route="/counter_example", title="Counter example")
def index() -> rx.Component:
    counter = Counter.create()
    other_component = rx.card(
        rx.vstack(rx.text("I only increment"), rx.text(OtherState.value)))
    counter.State.register_listener(
        OtherState.increment_when_counter_increments)

    counter_2 = Counter.create()
    return rx.container(
        rx.card(
            rx.hstack(
                rx.text("The counter:"),
                counter,
            ),
            rx.hstack(
                rx.text(
                    "Some other component that updates when the counter increments"),
                other_component,
            )
        ),
        rx.hstack(
            rx.text("Another counter that is separate"),
            counter_2,
        )
    )
