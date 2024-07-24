import reflex as rx

from typing import Any
import base64

from reflex_test.templates import template


class AudioRecorder(rx.Component):
    """Wrapper for react-audio-voice-recorder component."""

    # The React library to wrap.
    library = "react-audio-voice-recorder"

    # The React component tag.
    tag = "AudioRecorder"

    is_default = False

    def get_event_triggers(self) -> dict[str, Any]:
        return {
            **super().get_event_triggers(),
            "on_recording_complete": _on_recording_complete_signature,
        }


audio_recorder = AudioRecorder.create


def _on_recording_complete_signature(blob: Any):
    return [rx.Var.create_safe(f"extract_audio({blob})")]


class AudioState(rx.State):
    def recording_complete_callback(self, b64_str):
        decodedData = base64.b64decode(b64_str.split(",")[1])
        webmfile = rx.get_upload_dir() / "audio.webm"
        with open(webmfile, "wb") as file:
            file.write(decodedData)

    def update_recorded_audio(self, url: any):
        return [
            rx.call_script(
                f"""download_blob("{url}")""",
                callback=AudioState.recording_complete_callback,
            )
        ]


@template(route="/audio", title="Audio Recorder")
def index() -> rx.Component:
    return rx.center(
        rx.script("""function download_blob(url) {
                    console.log(url);
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', url, true);
                    xhr.responseType = 'blob';
                    return new Promise((resolve, reject) => {
                        xhr.onload = function(e) {
                            if (this.status == 200) {
                                var blob = this.response;
                                // console.log(blob);
                                // blob is now the blob that the object URL pointed to.
                                var reader = new window.FileReader();
                                reader.readAsDataURL(blob); 
                                reader.onloadend = function() {
                                    var base64 = reader.result;
                                    // base64 = base64.split(',')[1];
                                    // console.log(base64);
                                    resolve(base64);
                                }
                            }
                        };
                        xhr.send();
                    });
                  };
                """),
        rx.script("""function extract_audio(blob) {
                if (!(blob instanceof Blob)) {
                    console.error('Invalid argument type:', typeof blob);
                    throw new TypeError('Argument must be a Blob');
                }
                console.log('Extracting audio from type:', typeof blob);
                console.log('instance of Blob:', blob instanceof Blob);
                const url = URL.createObjectURL(blob);
                return url;
            };
            """),
        audio_recorder(
            id="audio_recorder",
            on_recording_complete=AudioState.update_recorded_audio,
            download_on_save_press=True,
        ),
    )
