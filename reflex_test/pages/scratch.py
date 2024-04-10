import asyncio

import reflex as rx

from reflex_test.templates import template


class DifferentState(rx.State):
    color: str = "red"
    _clicks: int = 0

    def change_color(self):
        self._clicks += 5
        self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]


class ScratchState(rx.State):
    color: str = "red"
    _clicks: int = 0

    def change_color(self):
        self._clicks += 1
        self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]
        yield DifferentState.change_color

    def sync_color_change_method(self):
        self._clicks += 1
        self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]
        # Does not work to yield another state change
        # yield DifferentState.change_color

    def change_color_by_method(self):
        self.sync_color_change_method()


    @rx.background
    async def async_change_color(self):
        print("Changing color async")
        async with self:
            self._clicks += 1
            self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]
        await asyncio.sleep(0.5)
        yield DifferentState.change_color
        await asyncio.sleep(0.5)
        async with self:
            self._clicks += 1
            self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]
        await asyncio.sleep(0.5)
        yield DifferentState.change_color

    async def async_color_change_method_with_self(self):
        async with self:
            self._clicks += 1
            self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]
        await asyncio.sleep(0.5)
        yield DifferentState.change_color

    async def async_color_change_method_without_self(self):
        self._clicks += 1
        self.color = ["red", "green", "blue", "yellow", "purple", "orange"][self._clicks % 6]
        yield
        await asyncio.sleep(0.5)
        yield DifferentState.change_color

    @rx.background
    async def async_change_color_by_method(self):
        async for v in self.async_color_change_method_with_self():
            yield v
        await asyncio.sleep(0.5)
        async with self:
            async for v in self.async_color_change_method_without_self():
                yield v

    async def directly_change_other_state(self):
        different_state = await self.get_state(DifferentState)
        different_state.color = "white"


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
            rx.card(
                rx.heading("Update other state directly"),
                rx.button("Change color", on_click=ScratchState.directly_change_other_state),
            ),
            rx.box(width="50em", height="10em", background_color=rx.color(DifferentState.color, alpha=False)),
            width="100%",
        ),

    )