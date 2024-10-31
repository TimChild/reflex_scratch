from reflex_test import styles

# Import all the pages.
from reflex_test.pages import *  # noqa: F403

import reflex as rx

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

# Create the app.
# app = rx.App(style=styles.base_style, head_components=[text_area_auto_expand_script])
app = rx.App(style=styles.base_style, head_components=[])
