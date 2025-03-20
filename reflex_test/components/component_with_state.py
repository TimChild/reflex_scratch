import asyncio
import random

import reflex as rx


class ComponentWithState(rx.ComponentState):
    text: str = "Hello, World!"

    def update(self):
        self.text = random.choice(["Hello, Universe!", "Hello, you!", "Hello, Galaxy!", "Hello, Multiverse!"])

    @rx.event(background=True)
    async def update_background(self):
        while True:
            async with self:
                self.text = random.choice(["Hello, Universe!", "Hello, you!", "Hello, Galaxy!", "Hello, Multiverse!"])
            await asyncio.sleep(1)

    @classmethod
    def get_component(cls, *children, **props) -> rx.Component:
        return rx.vstack(
            rx.text(cls.text),
            rx.button("Change State", on_click=cls.update),
            rx.button("Change State Background", on_click=cls.update_background),
            *children,
            **props,
        )


component_with_state = ComponentWithState.create
