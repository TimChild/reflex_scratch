import random

import reflex as rx


class ComponentWithState(rx.ComponentState):
    text: str = "Hello, World!"

    def update(self):
        self.text = random.choice(
            ["Hello, Universe!", "Hello, you!", "Hello, Galaxy!", "Hello, Multiverse!"]
        )

    @classmethod
    def get_component(cls, *children, **props) -> rx.Component:
        return rx.vstack(
            rx.text(cls.text),
            rx.button("Change State", on_click=cls.update),
            *children,
            **props,
        )



component_with_state = ComponentWithState.create