import time
from urllib.request import urlopen
from PIL import Image

import reflex as rx
import reflex_webcam as webcam

from reflex_test.templates import template

# Identifies a particular webcam component in the DOM
WEBCAM_REF = "webcam"


class WebcamState(rx.State):
    last_screenshot: Image.Image | None = None
    last_screenshot_timestamp: str = ""
    loading: bool = False

    def handle_screenshot(self, img_data_uri: str):
        """Webcam screenshot upload handler.
        Args:
            img_data_uri: The data uri of the screenshot (from upload_screenshot).
        """
        if self.loading:
            return
        self.last_screenshot_timestamp = time.strftime("%H:%M:%S")
        with urlopen(img_data_uri) as img:
            self.last_screenshot = Image.open(img)
            self.last_screenshot.load()
            # convert to webp during serialization for smaller size
            self.last_screenshot.format = "WEBP"  # type: ignore


def last_screenshot_widget() -> rx.Component:
    """Widget for displaying the last screenshot and timestamp."""
    return rx.box(
        rx.cond(
            WebcamState.last_screenshot,
            rx.fragment(
                rx.image(src=WebcamState.last_screenshot),
                rx.text(WebcamState.last_screenshot_timestamp),
            ),
            rx.center(
                rx.text("Click image to capture.", size="4"),
            ),
        ),
        height="270px",
    )


def webcam_upload_component(ref: str) -> rx.Component:
    """Component for displaying webcam preview and uploading screenshots.
    Args:
        ref: The ref of the webcam component.
    Returns:
        A reflex component.
    """
    return rx.vstack(
        webcam.webcam(
            id=ref,
            on_click=webcam.upload_screenshot(
                ref=ref,
                handler=WebcamState.handle_screenshot,  # type: ignore
            ),
        ),
        last_screenshot_widget(),
        width="320px",
        align="center",
    )


@template(route="/webcam", title="Webcam")
def index() -> rx.Component:
    return rx.fragment(
        rx.center(
            webcam_upload_component(WEBCAM_REF),
            padding_top="3em",
        ),
    )
