from typing import Any

import reflex as rx
from reflex_test.templates import template


def set_component_state_default(class_: type[rx.State], attr_name: str, value: Any) -> None:  # noqa: ANN401
    """Sets a new default value for the given attribute of the state class.

    Temporary solution for changing default behaviour of ComponentState from:
    https://github.com/reflex-dev/reflex/issues/3771

    Note: This is for use only when interacting with the `cls` object rather than the `self` used in event handlers.
    """
    class_.get_fields()[attr_name].default = value


class Item(rx.Base):
    item_name: str
    key: str


ITEMS = [
    Item(item_name="Hammer", key="hammer"),
    Item(item_name="Screwdriver", key="screwdriver"),
]


class MultiCheckbox(rx.ComponentState):
    available_options: list[Item] = []
    selected_items: list[Item] = []

    menu_open: bool = False

    def select_item(self, item: Item):
        if item in self.selected_items:
            self.selected_items.remove(item)

        else:
            self.selected_items.append(item)

    def set_menu_open(self, is_open: bool):
        self.menu_open = is_open

    @classmethod
    def get_component(cls, button_text: str, items: list[Item]) -> rx.Component:
        set_component_state_default(cls, "available_options", items)

        return rx.flex(
            rx.menu.root(
                rx.menu.trigger(rx.box(rx.button(button_text, on_click=lambda: cls.set_menu_open(True)))),
                rx.menu.content(
                    rx.text("Available Tools"),
                    rx.menu.separator(),
                    rx.foreach(
                        cls.available_options,
                        lambda item: rx.menu.item(
                            rx.checkbox(
                                item.item_name,
                                checked=cls.selected_items.contains(item.key, "key"),
                                on_change=lambda _: cls.select_item(item),
                            ),
                        ),
                    ),
                    on_pointer_down_outside=lambda: cls.set_menu_open(False),
                ),
                open=cls.menu_open,
            )
        )


def example() -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(
            rx.button("Options", variant="soft"),
        ),
        rx.menu.content(
            rx.menu.item("Edit", shortcut="⌘ E"),
            rx.menu.item("Duplicate", shortcut="⌘ D"),
            rx.menu.separator(),
            rx.menu.item("Archive", shortcut="⌘ N"),
            rx.menu.sub(
                rx.menu.sub_trigger("More"),
                rx.menu.sub_content(
                    rx.menu.item("Move to project…"),
                    rx.menu.item("Move to folder…"),
                    rx.menu.separator(),
                    rx.menu.item("Advanced options…"),
                ),
            ),
            rx.menu.separator(),
            rx.menu.item("Share"),
            rx.menu.item("Add to favorites"),
            rx.menu.separator(),
            rx.menu.item("Delete", shortcut="⌘ ⌫", color="red"),
        ),
    )


@template("/multi_checkbox", title="Multi checkbox")
def index() -> rx.Component:
    return rx.container(
        example(),
        rx.divider(),
        rx.card(
            rx.text("multi checkbox test"),
            rx.divider(),
            rx.button("test"),
            MultiCheckbox.create(button_text="Select tools", items=ITEMS),
        ),
    )
