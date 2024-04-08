from textwrap import dedent
from typing import Dict, Any
import reflex as rx
from reflex.vars import Var


class _AudioSaveEvent(rx.Base):
    event: Any
    blob: Any


def _on_recording_complete_signature(blob: Any) -> list[Any]:
    return [
        # e0.event,
        rx.Var.create_safe(f"extract_audio({blob})"),
    ]


# rx.Var.create_safe(f"serializeBlob({blob}).then(serializedString => {{return serializedString}}).catch(error => {{console.error('Error serializing blob:', error);}})"),


clientside_audio_url_script = dedent("""\
            const extract_audio = (blob) => {
            if (!(blob instanceof Blob)) {
                console.error('Invalid argument type:', typeof blob);
                throw new TypeError('Argument must be a Blob');
            }
            console.log('Extracting audio from type:', typeof blob);
            console.log('instance of Blob:', blob instanceof Blob);
            const url = URL.createObjectURL(blob);
            return url;
            };
            """)

# serialize_blob_promise = dedent("""\
#     function serializeBlob(blob) {
#       return new Promise((resolve, reject) => {
#         const reader = new FileReader();
#         reader.onload = function() {
#           // The result attribute contains the data as a base64 encoded string
#           resolve(reader.result);
#         };
#         reader.onerror = function(error) {
#           reject(error);
#         };
#         reader.readAsDataURL(blob);
#       });
#     }
#     """)

class AudioRecorder(rx.Component):
    """Wrapper for react-audio-voice-recorder component."""

    # The React library to wrap.
    library = "react-audio-voice-recorder"

    # The React component tag.
    tag = "AudioRecorder"

    # If the tag is the default export from the module, you can set is_default = True.
    # This is normally used when components don't have curly braces around them when importing.
    is_default = False

    # The props of the React component.
    # Note: when Reflex compiles the component to Javascript,
    # `snake_case` property names are automatically formatted as `camelCase`.
    # The prop names may be defined in `camelCase` as well.

    # Show waveform while recording
    show_visualizer: Var[bool] = True

    # Download audio client-side on save press
    download_on_save_press: Var[bool] = False

    def get_event_triggers(self) -> Dict[str, Any]:
        return {
            **super().get_event_triggers(),
            "on_recording_complete": _on_recording_complete_signature,
        }

    def _get_custom_code(self) -> str:
        return clientside_audio_url_script

    # def _get_hooks(self) -> str | None:
    #     if self.id is not None:
    #         return (
    #             super()._get_hooks() or ""
    #         ) + f"refs['audiorecorder_{self.id}'] = useRef(null)"
    #     return super()._get_hooks()


audio_recorder = AudioRecorder.create

# def upload_audio(ref: str, handler: rx.event.EventHandler):
#     """Helper to capture and upload an audio recording from an audio recorder component.
#     Args:
#         ref: The ref of the audio recorder component.
#         handler: The event handler that receives the audio recording.
#     """
#     return rx.call_script(
#         f"refs['audiorecorder_{ref}'].current.getRecording()",
#         callback=handler,
