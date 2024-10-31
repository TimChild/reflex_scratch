"""
2024-04-08 -- From masenf in discord

Helpful to see how javascript can be added to the page.
"""

import reflex as rx
from reflex_test.templates import template


def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Expandable Textarea"),
        rx.text_area(min_height="2.5em", width="80vw"),
        align="center",
        height="100vh",
    )


# https://stackoverflow.com/a/25621277
# text_area_auto_expand_script = rx.script("""
#         const tx = document.getElementsByTagName("textarea");
#         for (let i = 0; i < tx.length; i++) {
#         tx[i].setAttribute("style", "height:" + (tx[i].scrollHeight) + "px;overflow-y:hidden;");
#         tx[i].addEventListener("input", OnInput, false);
#         }
#
#         function OnInput() {
#         this.style.height = 'auto';
#         this.style.height = (this.scrollHeight) + "px";
#         }
#         """)

text_area_auto_expand_script = rx.script("""
        const tx = document.getElementsByTagName("textarea");
        for (let i = 0; i < tx.length; i++) {
        tx[i].setAttribute("style", "height:" + (tx[i].scrollHeight) + "px;overflow-y:auto;");
        tx[i].addEventListener("input", OnInput, false);
        }

        function OnInput() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + "px";
        }
        """)

# app = rx.App(
#     head_components=[
#         text_area_auto_expand_script,
#     ],
# )
# app.add_page(index)


class TextState(rx.State):
    text: str = ""


@template(
    route="/text_area_expand",
    title="expandable text area",
    # script_tags=[text_area_auto_expand_script],
)
def index() -> rx.Component:
    return rx.container(
        text_area_auto_expand_script,
        rx.heading("Testing expandable text area"),
        rx.text_area(
            # value=TextState.text,
            # on_change=TextState.set_text,
            placeholder="Enter text here",
            max_height="200px",
        ),
    )
