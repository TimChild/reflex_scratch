import random

import reflex as rx


class ComponentState(rx.State):
    text: str = "Hello, World!"

    def update(self):
        self.text = random.choice(["Hello, Universe!", "Hello, you!", "Hello, Galaxy!", "Hello, Multiverse!"])


def layout() -> rx.Component:
    return rx.box(
        rx.text("Hello, World!"),
        rx.text(ComponentState.text),
        rx.button("Change State",
                  on_click=ComponentState.update),
    )