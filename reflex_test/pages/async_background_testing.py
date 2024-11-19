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
    number: int = 0

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

    @rx.background
    async def increment_number(self):
        async with self:
            self.number = 10
        await asyncio.sleep(0.3)
        async with self:
            self.number = 20

    @rx.background
    async def start_several_tasks_via_yields(self):
        async with self:
            self.number = 0
        await asyncio.sleep(1)
        yield ScratchState.increment_number
        await asyncio.sleep(1)
        async with self:
            self.number = 1


class CacheTestState(rx.State):
    @rx.var(cache=True)
    def cached_str(self) -> str:
        return "cached sync str"

    # @rx.var(cache=True)
    # async def async_cached_str(self) -> str:
    #     return "cached async str"


@template(route="/async_background_testing", title="Async background testing")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Scratch page:"),
            rx.divider(),
            rx.card(
                rx.heading("Cache test"),
                rx.text(f"Cached str: {CacheTestState.cached_str}"),
                # rx.text(f'Async Cached str: {CacheTestState.async_cached_str}'),
            ),
            rx.divider(),
            rx.card(
                rx.heading("Update state directly"),
                rx.button("Change color", on_click=ScratchState.change_color),
                background_color=rx.color(ScratchState.color, alpha=True),
            ),
            rx.card(
                rx.heading("Update state from method call"),
                rx.button("Change color", on_click=ScratchState.change_color_by_method),
                background_color=rx.color(ScratchState.color, alpha=True),
            ),
            rx.card(
                rx.heading("Update state async background task"),
                rx.button("Change color", on_click=ScratchState.async_change_color),
                background_color=rx.color(ScratchState.color, alpha=True),
            ),
            rx.card(
                rx.heading("Update state async background task method call"),
                rx.button("Change color", on_click=ScratchState.async_change_color_by_method),
                background_color=rx.color(ScratchState.color, alpha=True),
            ),
            rx.card(
                rx.heading("Update other state directly"),
                rx.button("Change color", on_click=ScratchState.directly_change_other_state),
            ),
            rx.box(
                width="50em",
                height="10em",
                background_color=rx.color(DifferentState.color, alpha=False),
            ),
            rx.button(rx.text(ScratchState.number.to(str)), on_click=ScratchState.start_several_tasks_via_yields),
            width="100%",
        ),
    )
