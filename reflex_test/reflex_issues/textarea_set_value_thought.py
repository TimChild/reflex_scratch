import time

import reflex as rx


class SomeState(rx.State):
    submitted_text: str = ""

    # Ideally wouldn't need this
    current_value: str = ""

    # for demo only
    _valid_submission: bool = False

    @rx.var
    def submission_valid(self) -> bool:
        # This exact case might still be fixed by a cached_var, but I think there are cases where it wouldn't
        # Or there are just many other rx.vars for some reason
        if not self.submitted_text:
            return False

        # This is a placeholder for a backend check that could be expensive
        # e.g. `has_anyone_else_submitted_text(text) that has to check a database etc`
        time.sleep(1)
        self._valid_submission = not self._valid_submission
        return self._valid_submission

    def handle_form_submission(self, data: dict[str, str]):
        self.submitted_text = data["text"]

    def handle_update_text_area(self):
        # Ideally, something like this would be nice
        yield rx.set_value(ref="textarea_id", value="Starting text that could be loaded from db etc.")

    def handle_update_text_area_set_value(self):
        # Ideally wouldn't need this
        self.current_value = "Starting text that could be loaded from db etc."


@rx.page(route="/text_area", title="Text area example")
def index() -> rx.Component:
    return rx.container(
        rx.heading("Example"),
        rx.form(
            # Ideally would use this
            # rx.text_area(
            #     id="textarea_id",
            #     name="text",
            # ),
            rx.text_area(
                name="text",
                value=SomeState.current_value,
                on_change=SomeState.set_current_value,
            ),
            rx.button("Submit"),
            on_submit=SomeState.handle_form_submission,
        ),
        rx.cond(
            SomeState.submission_valid,
            rx.box("Valid submission", background_color="green"),
            rx.box("Invalid submission", background_color="red"),
        ),
        rx.text(f"Submitted text: {SomeState.submitted_text}"),
        rx.heading("Computed value:"),
        rx.text(SomeState.submission_valid),
        # Ideally would be able to use something like this
        # rx.button("Set starting text", on_click=SomeState.handle_update_text_area),
        rx.button("Set starting text", on_click=SomeState.handle_update_text_area_set_value),
    )
