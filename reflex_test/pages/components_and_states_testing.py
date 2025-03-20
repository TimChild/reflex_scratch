import abc
import asyncio
import logging
import random
from contextlib import asynccontextmanager
from typing import cast

import reflex as rx
from ..templates import template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

choices = ["a", "b", "c", "d", "e", "f", "g"]


class AnotherMixin(rx.State, mixin=True):  # , abc.ABC):
    mixin_value: int = 0

    def increment_mixin_sync_event(self):
        """Works as an event handler directly"""
        self.mixin_value += 1

    async def increment_mixin_async_event(self):
        """
        Works as an event handler directly and yields multiple events.
        Because it is not a background task, it blocks any other events from occurring
        """
        for _ in range(10):
            self.mixin_value += 1
            yield
            await asyncio.sleep(0.1)

    async def increment_mixin_background(self):
        """This one cannot be implemented as a @rx.event(background=True) directly in the mixin. But it can implement the logic
        i.e. using async with self.
        Then a very simple _event method can be added to the class that it is mixing into.
        """
        for i in range(10):
            async with self:
                self.mixin_value += 1
            await asyncio.sleep(0.1)

    @rx.event(background=True)
    @abc.abstractmethod
    async def increment_mixin_background_event(self):
        """Can't be mixed in directly because it doesn't get detected as a background task"""
        pass


class OptionalSelfMixin:
    """
    2024-04-29 This works, but the behaviour when calling method from another state is different to that when called
    from a background state. Many tasks overwrite each other without the async with self block.
    """

    @asynccontextmanager
    async def opt_self(self: rx.State, with_self: bool):
        if with_self:
            async with self:
                yield
        else:
            yield


class OtherState(rx.State):
    external_call_value: int = 0

    @rx.event(background=True)
    async def run_with_one_value(self):
        # async with self:
        # page_state = cast(PageState, await self.get_state(PageState))
        val = random.choice(choices)
        yield PageState.initialize_state(val, "")
        print(f"Tried to init val with: {val}")

    def run_with_second_value(self, data: dict):
        val = random.choice(choices)
        second_val = data["second_value"]

        # second_val = ', '.join([random.choice(choices) for _ in range(5)])
        yield PageState.initialize_state(val, second_val)
        print(f"Tried to init val with: {val}, second_val with: {second_val}")

    @rx.event(background=True)
    async def await_method_of_another_state_event(self):
        async with self:
            page_state = cast(PageState, await self.get_state(PageState))

            # These updates are tracked
            async for event in page_state.do_something_method():
                yield event

        # These are not
        async for event in page_state.do_something_method():
            yield event

    @classmethod
    async def method_to_be_called_from_external_state_background(
        cls, external_state: rx.State, with_self: bool = False
    ):
        """
        When called from another state, this acts like a regular async handler

        It can yield updates, and DOES NOT block the frontend as long as the `async with` parts are short!
        """
        for _ in range(10):
            async with external_state.opt_self(with_self):
                current_state = cast(OtherState, await external_state.get_state(OtherState))
                current_state.external_call_value += 1
            yield
            await asyncio.sleep(0.1)

        async with external_state.opt_self(with_self):
            another_other_state = cast(AnotherOtherState, await external_state.get_state(AnotherOtherState))
            another_other_state.value += 1

    @classmethod
    async def method_to_be_called_from_external_state_background_alternative(cls, external_state: rx.State):
        """
        Similar to above where the async with self is handled by the external state.
        However, the async with self block is broken at the first yield, so have to make sure anything that
        requires the async with block is done early (might be more difficult with nested functions?)

        Also, this DOES block the frontend (because the async with self has to be held open in the background event
        that calls it)
        """
        current_state = cast(OtherState, await external_state.get_state(OtherState))
        another_other_state = cast(AnotherOtherState, await external_state.get_state(AnotherOtherState))

        for _ in range(10):
            current_state.external_call_value += 1
            yield
            await asyncio.sleep(0.1)

        # Can't do this if called from background task because the yield above breaks the async with self block
        # another_other_state = cast(AnotherOtherState, await external_state.get_state(AnotherOtherState))
        another_other_state.value += 1

    def regular_event(self):
        """
        Does calling the regular event after the external_state_background event work (does it see the updated data)?
        """
        self.external_call_value += 1


class AnotherOtherState(rx.State):
    value: int = 0


class PageState(OptionalSelfMixin, AnotherMixin, rx.State):
    value: str = "a"
    second_value: str = ""

    external_call_value: int = 0

    @rx.event(background=True)
    async def increment_mixin_background_event(self):
        await self.increment_mixin_background()

    def initialize_state(self, value: str, second_value: str = None):
        logger.info(f"Setting value to {value}")
        self.value = value
        self.second_value = second_value

    async def do_something_method(self, with_self=False):
        async with self.opt_self(with_self):
            s: str = (self.second_value * 2)[:15]
            s = "".join(reversed(s))
            self.second_value = s
        yield

        for i in range(10):
            async with self.opt_self(with_self):
                self.value = f"{self.value}, {random.choice(choices)}"
            yield
            await asyncio.sleep(0.03)

    @rx.event(background=True)
    async def do_something_event(self):
        # await self.do_something_method_background()
        async for event in self.do_something_method(with_self=True):
            yield event

    @rx.event(background=True)
    async def call_external_method_background_event(self):
        """
        This behaves like a normal background handler except that when yielding events from the OtherState it
        behaves like a regular handler (blocks frontend)
        """
        async with self:
            self.external_call_value += 1
        await asyncio.sleep(0.5)
        # This way does not block the frontend
        async for event in OtherState.method_to_be_called_from_external_state_background(self, with_self=True):
            yield event
        await asyncio.sleep(0.5)
        async with self:
            self.external_call_value += 10
        await asyncio.sleep(0.5)
        # This way blocks the frontend until finished
        async with self:
            async for event in OtherState.method_to_be_called_from_external_state_background_alternative(self):
                yield event
        await asyncio.sleep(0.5)
        async with self:
            self.external_call_value += 1

    async def call_external_method_event(self):
        """
        This behaves like a normal handler (blocking frontend until finished)
        """
        self.external_call_value += 1
        await asyncio.sleep(0.5)
        async for event in OtherState.method_to_be_called_from_external_state_background(self):
            yield event
        await asyncio.sleep(0.5)
        self.external_call_value += 10
        await asyncio.sleep(0.5)
        async for event in OtherState.method_to_be_called_from_external_state_background_alternative(self):
            yield event
        await asyncio.sleep(0.5)
        self.external_call_value += 1


@template(route="/component_and_state_testing", title="Component vs State")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.text("Component vs state"),
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("The State version:"),
                    rx.text(f"PageState.value: {PageState.value}"),
                    rx.text(f"PageState.second_value: {PageState.second_value}"),
                ),
                rx.button("Yield event from OtherState with one value", on_click=OtherState.run_with_one_value),
                # rx.button('Set via other with second value', on_click=OtherState.run_with_second_value),
                rx.button("PageState.do_something_event", on_click=PageState.do_something_event),
                rx.form(
                    rx.hstack(
                        rx.input(name="second_value", placeholder="Second value", width="200px"),
                        rx.button("OtherState.run_with_second_value"),
                        wrap="wrap",
                    ),
                    on_submit=OtherState.run_with_second_value,
                ),
                rx.button(
                    "OtherState.await_method_of_another_state_event",
                    on_click=OtherState.await_method_of_another_state_event,
                ),
                rx.divider(),
                rx.text(f"Mixin value: {PageState.mixin_value}"),
                rx.button("Increment mixin sync", on_click=PageState.increment_mixin_sync_event),
                rx.button("Increment mixin async", on_click=PageState.increment_mixin_async_event),
                rx.button("Increment mixin background", on_click=PageState.increment_mixin_background_event),
                rx.divider(),
                rx.heading("External Call Testing", size="5"),
                rx.button(
                    "OtherState.call_external_method_background_event",
                    on_click=PageState.call_external_method_background_event,
                ),
                rx.button("PageState.call_external_method_event", on_click=PageState.call_external_method_event),
                rx.text(f"PageState.external_call_value: {PageState.external_call_value}"),
                rx.text(f"OtherState.external_call_value: {OtherState.external_call_value}"),
                rx.text(f"AnotherOtherState.value: {AnotherOtherState.value}"),
                rx.button("OtherState.regular_event", on_click=OtherState.regular_event),
            ),
        ),
    )
