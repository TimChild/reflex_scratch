import reflex as rx
from typing import Any

from reflex.components.component import Component


class MultiSelectComponent(Component):
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


multiselect = MultiSelectComponent.create


class MultiSelectState(rx.State):
    selected: list[dict[str, str]] = []

    def handle_change(self, change: list[dict[str, str]]):
        print(f"Change: {change}")
        self.selected = change

    @rx.cached_var
    def selected_values(self) -> str:
        print(self.selected)
        return ", ".join([d["value"] for d in self.selected])


# @rx.page(route="/multi_select", title="Multi Select")
# def index() -> rx.Component:
#     return rx.box(
#         multiselect(
#             options=[{'value': 'opt1', 'label': 'Option 1'}, {'value': 'opt2', 'label': 'Option 2'}],
#             value=MultiSelectState.selected,
#             on_change=MultiSelectState.handle_change
#         ),
#     )
