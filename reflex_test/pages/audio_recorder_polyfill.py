from typing import cast
from urllib.request import urlopen

import reflex as rx

from reflex_audio_capture import AudioRecorderPolyfill, get_codec, strip_codec_part

from reflex_test.templates.template import template


REF = "myaudio"


class State(rx.State):
    """The app state."""

    has_error: bool = False
    processing: bool = False
    transcript: list[str] = []
    timeslice: int = 0
    device_id: str = ""
    use_mp3: bool = True

    async def on_data_available(self, chunk: str):
        codec = get_codec(chunk)
        assert codec is not None
        mime_type, _, codec = codec.partition(";")
        audio_type = mime_type.partition("/")[2]
        if audio_type == "mpeg":
            audio_type = "mp3"
        print(len(chunk), mime_type, codec, audio_type)
        with urlopen(strip_codec_part(chunk)) as audio_data:
            try:
                self.processing = True
                yield rx.toast.info("Starting processing")
                # transcription = await client.audio.transcriptions.create(
                #     model="whisper-1",
                #     file=("temp." + audio_type, audio_data.read(), mime_type),
                # )
            except Exception:
                self.has_error = True
                yield capture.stop()
                raise
            finally:
                self.processing = False
            # self.transcript.append(transcription.text)
            self.transcript.append("...new text...")

    def set_timeslice(self, value):
        self.timeslice = value[0]

    def set_device_id(self, value):
        self.device_id = value
        yield capture.stop()

    def on_error(self, err):
        print(err)

    def on_load(self):
        # We can start the recording immediately when the page loads
        return capture.start()


capture: AudioRecorderPolyfill = cast(
    AudioRecorderPolyfill,
    AudioRecorderPolyfill.create(
        id=REF,
        on_data_available=State.on_data_available,
        on_error=State.on_error,
        timeslice=State.timeslice,
        device_id=State.device_id,
        use_mp3=State.use_mp3,
    ),
)


def input_device_select():
    return rx.select.root(
        rx.select.trigger(placeholder="Select Input Device"),
        rx.select.content(
            rx.foreach(
                capture.media_devices,
                lambda device: rx.cond(
                    device.deviceId & device.kind == "audioinput",
                    rx.select.item(device.label, value=device.deviceId),
                ),
            ),
        ),
        on_change=State.set_device_id,
    )


@template(route="/audio_recorder", title="Audio recorder")
def index() -> rx.Component:
    # TODO: Don't know why I can't get this to work here... This is almost a direct copy from https://github.com/masenf/reflex-audio-capture/blob/47c032d393a96bfc34a7ac6d2aba3027c932c063/audio_capture_demo/audio_capture_demo/audio_capture_demo.py
    return rx.container(
        rx.vstack(
            rx.heading("OpenAI Whisper Demo"),
            rx.card(
                rx.vstack(
                    f"Timeslice: {State.timeslice} ms",
                    rx.slider(
                        min=0,
                        max=10000,
                        value=[State.timeslice],
                        on_change=State.set_timeslice,
                    ),
                    rx.cond(
                        capture.media_devices,
                        input_device_select(),
                    ),
                ),
            ),
            capture,
            rx.text(f"Recorder Status: {capture.recorder_state}"),
            rx.cond(
                capture.is_recording,
                rx.button("Stop Recording", on_click=capture.stop()),
                rx.button(
                    "Start Recording",
                    on_click=capture.start(),
                ),
            ),
            rx.card(
                rx.text("Transcript"),
                rx.divider(),
                rx.foreach(
                    State.transcript,
                    rx.text,
                ),
                rx.cond(
                    State.processing,
                    rx.text("..."),
                ),
            ),
            style=rx.Style({"width": "100%", "> *": {"width": "100%"}}),
        ),
        size="1",
        margin_y="2em",
    )
