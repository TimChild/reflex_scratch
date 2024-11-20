import reflex as rx
from reflex_audio_capture import AudioRecorderPolyfill

from reflex_test.templates import template


class AudioState(rx.State):
    timeslice: int = 0

    # on_data_available
    @rx.event()
    def on_data_available(self, data):
        print(data)

    @rx.event()
    def on_error(self, error):
        print(error)


#
#
# module_audio_recorder = AudioRecorderPolyfill.create(
#     id="test-audio-recorder",
#     on_data_available=AudioState.on_data_available,
#     # on_error=AudioState.on_error,
#     # timeslice=AudioState.timeslice,
#     timeslice=10,
# )


@template(route="/audio_recorder", title="Audio recorder")
def index() -> rx.Component:
    return rx.text("2024-11-19 -- not currently working -- see https://github.com/orgs/reflex-dev/discussions/2300")

    # capture = AudioRecorderPolyfill.create(
    #     id="my_audio_recorder",
    #     on_data_available=AudioState.on_data_available,
    #     on_error=AudioState.on_error,
    #     timeslice=AudioState.timeslice,
    # )
    # return rx.vstack(
    #     capture,
    #     rx.cond(
    #         capture.is_recording,
    #         rx.button("Stop Recording", on_click=capture.stop),
    #         rx.button("Start Recording", on_click=capture.start),
    #     ),
    # )

    # return rx.container(
    #     rx.vstack(
    #         rx.hstack(
    #             rx.text("Audio recorder"),
    #             module_audio_recorder,
    #             rx.cond(
    #                 module_audio_recorder.is_recording,
    #                 rx.button("Stop recording", on_click=module_audio_recorder.stop),
    #                 rx.button("Start recording", on_click=module_audio_recorder.start),
    #             ),
    #         )
    #     ),
    # )
