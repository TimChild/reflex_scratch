import reflex as rx

from reflex_test.templates import template

from ..components.component_with_state import ComponentState
from ..components import component_with_state_layout



@template(route="/component_with_state", title="Component with State", on_load=[ComponentState.update])
def index() -> rx.Component:
    return rx.container(
        rx.heading('Component with State page:'),
        component_with_state_layout(),
    )