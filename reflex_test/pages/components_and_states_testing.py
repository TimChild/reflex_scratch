import abc
import asyncio
import logging
import random
from contextlib import asynccontextmanager
from typing import cast

import reflex as rx
from reflex import Component
from ..templates import template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

choices = ['a', 'b', 'c', 'd', 'e', 'f', 'g']



class AnotherMixin(rx.Base):#, abc.ABC):
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
        """This one cannot be implemented as a @rx.background directly in the mixin. But it can implement the logic
        i.e. using async with self.
        Then a very simple _event method can be added to the class that it is mixing into.
        """
        for i in range(10):
            async with self:
                self.mixin_value += 1
            await asyncio.sleep(0.1)

    @abc.abstractmethod
    async def increment_mixin_background_event(self):
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


class PageState(OptionalSelfMixin, AnotherMixin, rx.State):

    value: str = 'a'
    second_value: str = ''

    @rx.background
    async def increment_mixin_background_event(self):
        await self.increment_mixin_background()

    # def increment_mixin_value_event(self):
    # #     self.mixin_value += 1
    #     return self.increment_mixin_value_method()

    def initialize_state(self, value: str, second_value: str = None):
        logger.info(f"Setting value to {value}")
        self.value = value
        self.second_value = second_value


    async def do_something_method(self, with_self=False):
        async with self.opt_self(with_self):
            s: str = (self.second_value*2)[:15]
            s = ''.join(reversed(s))
            self.second_value = s
        yield

        for i in range(10):
            async with self.opt_self(with_self):
                self.value = f'{self.value}, {random.choice(choices)}'
            yield
            await asyncio.sleep(0.03)

    @rx.background
    async def do_something_event(self):
        # await self.do_something_method_background()
        async for event in self.do_something_method(with_self=True):
            yield event



class OtherState(rx.State):
    @rx.background
    async def run_with_one_value(self):
        # async with self:
            # page_state = cast(PageState, await self.get_state(PageState))
        val = random.choice(choices)
        yield PageState.initialize_state(val, '')
        print(f"Tried to init val with: {val}")

    def run_with_second_value(self, data: dict):
        val = random.choice(choices)
        second_val = data['second_value']

        # second_val = ', '.join([random.choice(choices) for _ in range(5)])
        yield PageState.initialize_state(val, second_val)
        print(f"Tried to init val with: {val}, second_val with: {second_val}")

    @rx.background
    async def await_method_of_another_state_event(self):
        async with self:
            page_state = cast(PageState, await self.get_state(PageState))

        async for event in page_state.do_something_method():
            yield event



class ExampleComponent(rx.Component):
    value: rx.Var[str] = 'a'

    @classmethod
    def create(cls, on_click, *children, **props) -> Component:
        super().create(*children, **props)
        return rx.card(
            rx.heading("Example Component", size="2"),
            rx.text(f'Selected value is: {cls.value}'),
            *children,
            **props
        )

@template(route="/component_and_state_testing", title="Component vs State")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.text(f'Component vs state'),
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("The State version:"),
                    rx.text(f'PageState.value: {PageState.value}'),
                    rx.text(f'PageState.second_value: {PageState.second_value}'),
                ),
                rx.button('Yield event from OtherState with one value', on_click=OtherState.run_with_one_value),
                # rx.button('Set via other with second value', on_click=OtherState.run_with_second_value),
                rx.button('PageState.do_something_event', on_click=PageState.do_something_event),
                rx.form(
                    rx.hstack(
                        rx.input(name='second_value', placeholder='Second value', width="200px"),
                        rx.button('OtherState.run_with_second_value'),
                        wrap="wrap",
                    ),
                    on_submit=OtherState.run_with_second_value
                ),
                rx.button('OtherState.await_method_of_another_state_event', on_click=OtherState.await_method_of_another_state_event),
                rx.divider(),
                rx.text(f"Mixin value: {PageState.mixin_value}"),
                rx.button('Increment mixin sync', on_click=PageState.increment_mixin_sync_event),
                rx.button('Increment mixin async', on_click=PageState.increment_mixin_async_event),
                rx.button('Increment mixin background', on_click=PageState.increment_mixin_background_event),

            ),
            rx.divider(),

        ),
    )