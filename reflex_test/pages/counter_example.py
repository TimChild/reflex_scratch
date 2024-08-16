import reflex as rx

from reflex_test.templates.template import template

class Counter(rx.ComponentState):
    # Define vars that change.
    count: int = 0

    # Define event handlers.
    def increment(self):
        self.count += 1

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

@template(route="/counter_example", title="Counter example")
def index() -> rx.Component:
    return rx.container(
        Counter.create(),
    )

