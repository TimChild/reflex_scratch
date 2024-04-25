import asyncio
import logging
import random
from typing import cast

import reflex as rx
from reflex import Component
from reflex_audio_capture import MediaDeviceInfo, AudioRecorderPolyfill
from ..templates import template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

choices = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

class PageState(rx.State):
    value: str = 'a'
    second_value: str = ''

    def initialize_state(self, value: str, second_value: str = None):
        logger.info(f"Setting value to {value}")
        self.value = value
        self.second_value = second_value

    @rx.background
    async def do_something(self):
        async with self:
            s: str = (self.second_value*2)[:15]
            s = ''.join(reversed(s))
            self.second_value = s

        for i in range(10):
            async with self:
                self.value = f'{self.value}, {random.choice(choices)}'
            await asyncio.sleep(0.03)




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


class AudioState(rx.State):
    # on_data_available
    def on_data_available(self, data):
        print(data)



module_audio_recorder = AudioRecorderPolyfill.create(
    id='test-audio-recorder',
    on_data_available=AudioState.on_data_available,
    # on_error=AudioState.on_error,
    # timeslice=AudioState.timeslice,
    timeslice=10,
)

@template(route="/component_and_state_testing", title="Component vs State")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.text(f'Component vs state'),
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("The State version:"),
                    rx.text(f'Selected value is: {PageState.value}'),
                    rx.text(f'Second value is: {PageState.second_value}'),
                ),
                rx.button('Set via other with one value', on_click=OtherState.run_with_one_value),
                # rx.button('Set via other with second value', on_click=OtherState.run_with_second_value),
                rx.button('Do something', on_click=PageState.do_something),
                rx.form(
                    rx.input(name='second_value', placeholder='Second value'),
                    rx.button('submit'),
                    on_submit=OtherState.run_with_second_value
                )
            ),
            rx.divider(),


            # ExampleComponent.create(),
            # rx.divider(),
            # rx.hstack(
            #     rx.text('Audio recorder'),
            #     module_audio_recorder,
            #     rx.cond(
            #         module_audio_recorder.is_recording,
            #         rx.button('Stop recording', on_click=module_audio_recorder.stop),
            #         rx.button('Start recording', on_click=module_audio_recorder.start),
            #     ),
            # )
        ),
    )