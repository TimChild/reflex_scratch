
import reflex as rx

from ..components import audio_recorder
from ..templates import template


class AudioState(rx.State):
    audio_recorded: str = ""
    transcribed_audio: str = ""

    def update_recorded_audio(self, audio_data: str):
        print(f'Event: , Audio data: {audio_data}')
        self.audio_recorded = str(audio_data)
        # return AudioState.transcribe_audio

    # async def transcribe_audio(self):
    #     transcription = await external_transcription_service(self.audio_recorded)
    #     self.transcribed_audio = transcription
    #     
    # async def stream_transcribe_audio(self, audio_chunk):
    #     transcription = await external_transcription_service(audio_chunk)
    #     self.transcribed_audio += transcription


def audio_component() -> rx.Component:
    return rx.fragment(
        audio_recorder.audio_recorder(
            # id="audio_recorder",
            on_recording_complete=AudioState.update_recorded_audio,
            # on_audio_chunk=AudioState.stream_transcribe_audio,  # << Ideally would actually use something like this
        ),
        rx.cond(
            AudioState.audio_recorded,
            rx.box(
                rx.text(f'Audio: {AudioState.audio_recorded}'),
                rx.text(f'Transcription: {AudioState.transcribed_audio}'),
                rx.audio(url=AudioState.audio_recorded, controls=True, width="100%")
            ),
            rx.text("Click to record audio."),
        ),
    )


@template(route="/audio", title="Audio Recorder")
def index() -> rx.Component:
    return rx.box(
        audio_component(),
        width="320px",
        align="center",
    )
