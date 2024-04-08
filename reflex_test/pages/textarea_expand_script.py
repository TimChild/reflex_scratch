"""
2024-04-08 -- From masenf in discord

Helpful to see how javascript can be added to the page.
"""
import reflex as rx


def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Expandable Textarea"),
        rx.text_area(min_height="2.5em", width="80vw"),
        align="center",
        height="100vh",
    )


app = rx.App(head_components=[
    ## https://stackoverflow.com/a/25621277
    rx.script("""
        const tx = document.getElementsByTagName("textarea");
        for (let i = 0; i < tx.length; i++) {
        tx[i].setAttribute("style", "height:" + (tx[i].scrollHeight) + "px;overflow-y:hidden;");
        tx[i].addEventListener("input", OnInput, false);
        }

        function OnInput() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + "px";
        }
        """)
    ],
)
app.add_page(index)
