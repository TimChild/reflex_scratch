import base64
import uuid
from typing import Any

import reflex as rx

from ..components import audio_recorder
from ..components.audio_recorder import clientside_audio_url_script
from ..templates import template


class MyAudioState(rx.State):
    audio_url: str = ""
    save_path: str = ""
    transcribed_audio: str = ""

    def update_from_url(self, url: str):
        print(f"Event: , Audio url: {url}")
        self.audio_url = str(url)
        return [
            rx.call_script(
                f"""download_blob("{url}")""", callback=MyAudioState.save_audio
            )
        ]
        # return AudioState.transcribe_audio

    def save_audio(self, b64_str):
        decodedData = base64.b64decode(b64_str.split(",")[1])
        webmfile = rx.get_upload_dir() / f"audio_{uuid.uuid4().hex[:4]}.webm"
        self.save_path = str(webmfile)
        with open(webmfile, "wb") as file:
            file.write(decodedData)

    # async def transcribe_audio(self):
    #     transcription = await external_transcription_service(self.audio_recorded)
    #     self.transcribed_audio = transcription
    #
    # async def stream_transcribe_audio(self, audio_chunk):
    #     transcription = await external_transcription_service(audio_chunk)
    #     self.transcribed_audio += transcription


def show_info(label: str, value: Any) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.heading(label, size="2"),
            rx.divider(),
            rx.text(value, max_height="200px", overflow="auto"),
            spacing="2",
        ),
    )


@template(route="/my_audio", title="My Audio Recorder")
def index() -> rx.Component:
    return rx.box(
        rx.script(clientside_audio_url_script),
        rx.heading("My Audio Recorder", size="5"),
        audio_recorder.audio_recorder(
            # id="audio_recorder",
            on_recording_complete=MyAudioState.update_from_url,
            # on_audio_chunk=AudioState.stream_transcribe_audio,  # << Ideally would actually use something like this
            download_on_save_press=True,
        ),
        rx.vstack(
            show_info("transcribed_audio", MyAudioState.transcribed_audio),
            show_info("audio_url", MyAudioState.audio_url),
            show_info("save_path", MyAudioState.save_path),
            rx.divider(),
            # rx.text(f'Transcription: {MyAudioState.transcribed_audio}'),
            rx.audio(url=MyAudioState.audio_url, controls=True, width="100%"),
            width="100%",
        ),
        width="320px",
        align="center",
    )
