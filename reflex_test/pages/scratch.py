import asyncio

import reflex as rx

from reflex_test.templates import template


class ScratchState(rx.State):
    color: str = "red"
    _clicks: int = 0

    def change_color(self):
        self._clicks += 1
        self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]

    def change_color_by_method(self):
        self.change_color()

    @rx.background
    async def async_change_color(self):
        print("Changing color async")
        async with self:
            self._clicks += 1
            self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]
        await asyncio.sleep(0.5)
        async with self:
            self._clicks += 1
            self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]

    async def color_change_method(self):
        async with self:
            self._clicks += 1
            self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]

    @rx.background
    async def async_change_color_by_method(self):
        await self.color_change_method()
        await asyncio.sleep(0.5)
        await self.color_change_method()

@template(route="/scratch", title="Scratch")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading('Scratch page:'),
            rx.divider(),
            rx.card(
                rx.heading("Update state directly"),
                rx.button("Change color", on_click=ScratchState.change_color),
                background_color=rx.color(ScratchState.color, alpha=True)
            ),
            rx.card(
                rx.heading("Update state from method call"),
                rx.button("Change color", on_click=ScratchState.change_color_by_method),
                background_color=rx.color(ScratchState.color, alpha=True)
            ),
            rx.card(
                rx.heading("Update state async background task"),
                rx.button("Change color", on_click=ScratchState.async_change_color),
                background_color=rx.color(ScratchState.color, alpha=True)
            ),
            rx.card(
                rx.heading("Update state async background task method call"),
                rx.button("Change color", on_click=ScratchState.async_change_color_by_method),
                background_color=rx.color(ScratchState.color, alpha=True)
            ),
            width="100%",
        ),

    )