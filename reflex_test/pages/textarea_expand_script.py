"""
2024-04-08 -- From masenf in discord

Helpful to see how javascript can be added to the page.
"""

import reflex as rx
from reflex.components.radix.themes.components.text_area import TextArea
from reflex_test.templates import template
from reflex.utils import imports
from lorem import sentence
import random


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


# class AutoExpandTextarea(TextArea):
#     """A textarea component that auto-expands based on its content."""
#
#     def add_imports(self) -> imports.ImportDict:
#         """Add the necessary imports for the component."""
#         return {
#             "react": [imports.ImportVar(tag="useEffect"), imports.ImportVar(tag="useRef")],
#         }
#
#     def add_custom_code(self) -> list[str]:
#         return [
#             f"""
#         (function() {{
#             const text_area = document.getElementById('{textarea_id}');
#             if (!text_area) return;
#
#             // Ensure the OnInput function is defined only once
#             if (!text_area.dataset.autoExpandInitialized) {{
#                 text_area.style.height = 'auto';
#                 text_area.style.height = (text_area.scrollHeight) + "px";
#                 text_area.style.overflowY = "auto";
#
#                 function OnInput() {{
#                     this.style.height = 'auto';
#                     this.style.height = (this.scrollHeight) + "px";
#                 }}
#
#                 text_area.addEventListener("input", OnInput, false);
#
#                 // Mark it as initialized
#                 text_area.dataset.autoExpandInitialized = "true";
#             }}
#         }})();
#     """
#         ]
#
#     def add_hooks(self) -> list[str | rx.Var]:
#         """Add the hooks for the component."""
#         return [
#             """
#             const textareaRef = useRef(null);
#
#             useEffect(() => {
#                 const textarea = textareaRef.current;
#                 if (textarea) {
#                     textarea.style.height = 'auto';
#                     textarea.style.height = `${textarea.scrollHeight}px`;
#                 }
#             }, [value]); // Adjust height whenever 'value' changes
#
#             return { ref: textareaRef };
#             """
#         ]


class TextState(rx.State):
    text: str = ""

    @rx.event()
    def set_text(self, val: str):
        self.text = val

    @rx.event()
    def update_text_value(self):
        self.text = "\n\n".join([sentence() for _ in range(random.randint(1, 5))])


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
            value=TextState.text,
            on_change=TextState.set_text,
            placeholder="Enter text here",
            max_height="200px",
        ),
        # AutoExpandTextarea.create(value=TextState.text, on_change=TextState.set_text),
        rx.button("update text", on_click=TextState.update_text_value),
    )
