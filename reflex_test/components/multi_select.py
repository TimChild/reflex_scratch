from typing import Any

import reflex as rx


class MultiSelectComponent(rx.Component):
    library = "react-select"
    tag = "Select"
    is_default = True
    value: rx.Var[list[str]] = []
    options: rx.Var[list[dict[str, str]]] = []
    is_multi: rx.Var[bool] = True
    is_searchable: rx.Var[bool] = True

    def get_event_triggers(self) -> dict[str, Any]:
        return {
            **super().get_event_triggers(),
            "on_change": lambda e0: [e0],
        }


class MultiSelectComponentState(rx.ComponentState):
    component_state_value: list[dict[str, str]] = []

    @classmethod
    def get_component(cls, *children, **props) -> rx.Component:
        on_change = props.pop("on_change", [])
        if not isinstance(on_change, list):
            on_change = [on_change]

        value = props.get("value", None)
        if value is None:
            value = cls.component_state_value
            on_change = [cls.set_component_state_value, *on_change]
        else:
            if not on_change:
                raise ValueError("MultiSelectComponent requires an on_change event handler if value is set.")

        return MultiSelectComponent.create(
            *children,
            value=value,
            on_change=on_change,
            **props,
        )


multiselect = MultiSelectComponentState.create

# @rx.page(route="/multi_select", title="Multi Select")
# def index() -> rx.Component:
#     return rx.box(
#         multiselect(
#             options=[{'value': 'opt1', 'label': 'Option 1'}, {'value': 'opt2', 'label': 'Option 2'}],
#             value=MultiSelectState.selected,
#             on_change=MultiSelectState.handle_change
#         ),
#     )
