"""The settings page."""

from reflex_test.templates import ThemeState, template

import reflex as rx


@template(route="/settings", title="Settings")
def settings() -> rx.Component:
    """The settings page.

    Returns:
        The UI for the settings page.
    """
    return rx.vstack(
        rx.heading("Settings", size="8"),
        rx.hstack(
            rx.text("Dark mode: "),
            rx.color_mode.switch(),
        ),
        rx.hstack(
            rx.text("Theme color: "),
            rx.select(
                [
                    "tomato",
                    "red",
                    "ruby",
                    "crimson",
                    "pink",
                    "plum",
                    "purple",
                    "violet",
                    "iris",
                    "indigo",
                    "blue",
                    "cyan",
                    "teal",
                    "jade",
                    "green",
                    "grass",
                    "brown",
                    "orange",
                    "sky",
                    "mint",
                    "lime",
                    "yellow",
                    "amber",
                    "gold",
                    "bronze",
                    "gray",
                ],
                value=ThemeState.accent_color,
                on_change=ThemeState.set_accent_color,
            ),
        ),
        rx.divider(),
        rx.text("More settings coming soon!"),
    )
