import reflex as rx

from reflex_test.templates import template


@template(route="/markdown_with_copy", title="Markdown with copy")
def index() -> rx.Component:
    # return rx.code_block("def foo():\n    pass", can_copy=True)
    return rx.markdown(
        """
        Some text where the code part should have a copy button.

        `inline code probably doesnt`

        ```python
        but this should
        def foo():
            pass
        ```

        did it? --- Well, not for now, because setting can_copy=True results in an error.
        """,
        component_map={
            "codeblock": lambda text, **props: rx.fragment(rx.code_block(
                text, **props, can_copy=False))

        }
    )
