import reflex as rx
from reflex_audio_capture import AudioRecorderPolyfill

from reflex_test.templates import template


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
                rx.text('Audio recorder'),
                module_audio_recorder,
                rx.cond(
                    module_audio_recorder.is_recording,
                    rx.button('Stop recording', on_click=module_audio_recorder.stop),
                    rx.button('Start recording', on_click=module_audio_recorder.start),
                ),
            )
        ),
    )
