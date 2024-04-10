from textwrap import dedent
from typing import Dict, Any
import reflex as rx
from reflex.utils.format import format_event_chain, for
from reflex.vars import Var


def _on_recording_complete_signature(blob: Any) -> list[Any]:
    return [
        rx.Var.create_safe(f"audio_blob_to_url({blob})"),
        # rx.Var.create_safe(f"extract_audio({blob})")
    ]


clientside_audio_url_script = dedent("""\
            const audio_blob_to_url = (blob) => {
            if (!(blob instanceof Blob)) {
                console.error('Invalid argument type:', typeof blob);
                throw new TypeError('Argument must be a Blob');
            }
            console.log('Extracting audio from type:', typeof blob);
            console.log('instance of Blob:', blob instanceof Blob);
            const url = URL.createObjectURL(blob);
            return url;
            };
            
            function download_blob(url) {
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
            """)


# """
#             function extract_audio(blob) {
#                 console.log(blob);
#                 return new Promise((resolve, reject) => {
#                     var reader = new window.FileReader();
#                     reader.readAsDataURL(blob);
#                     reader.onloadend = function() {
#                         var base64 = reader.result;
#                         resolve(base64);
#                     }
#                 });
#             };
# """

class AudioRecorder(rx.Component):
    """Wrapper for react-audio-voice-recorder component."""

    # The React library to wrap.
    library = "react-audio-voice-recorder"

    # The React component tag.
    tag = "AudioRecorder"

    # If the tag is the default export from the module, you can set is_default = True.
    # This is normally used when components don't have curly braces around them when importing.
    is_default = False

    # Show waveform while recording
    show_visualizer: Var[bool] = True

    # Download audio client-side on save press
    download_on_save_press: Var[bool] = False

    def get_event_triggers(self) -> Dict[str, Any]:
        return {
            **super().get_event_triggers(),
            "on_recording_complete": _on_recording_complete_signature,
        }

    def _get_hooks(self) -> str | None:
        pass

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
