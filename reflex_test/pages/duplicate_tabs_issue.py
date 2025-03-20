import asyncio
import reflex as rx
from reflex_test.templates import template


class State(rx.State):
    state_value: str = "Initial value"

    @rx.event(background=True)
    async def do_something(self):
        async with self:
            self.state_value = "Initial change"
        await asyncio.sleep(2)
        async with self:
            self.state_value = "Final change"


@template(route="/duplicate_tabs_issue", title="Duplicate tabs issue")
# @rx.page(route="/duplicate_tabs_issue", title="Duplicate tabs issue")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.markdown("Minimal example to demonstrate issues with duplicated tab in Chrome."),
            rx.markdown("`state.router.session.client_token` is not unique per tab when tab."),
            rx.text(f"state.router.session.client_token: {rx.State.router.session.client_token}"),
            rx.markdown("However, `state.router.session.session_id` does remain unique per tab."),
            rx.text(f"state.router.session.session_id: {rx.State.router.session.session_id}"),
            rx.divider(),
            rx.text("Somehow the tabs interfere with each other during background tasks."),
            rx.text(
                "Expect to see 'Initial change' followed by 'Final change' after 2 seconds. But that doesn't happen if the button is clicked in the other tab before the first event finishes."
            ),
            rx.button("Do something", on_click=State.do_something),
            rx.text(f"State.state_value: {State.state_value}"),
        )
    )
