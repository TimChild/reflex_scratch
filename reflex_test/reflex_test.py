"""Welcome to Reflex!."""

from reflex_test import styles

# Import all the pages.
from reflex_test.pages import *  # noqa: F403

import reflex as rx


class EmptyState(rx.State):
    """Define empty state to allow access to rx.State.router."""


# Create the app.
app = rx.App(style=styles.base_style)
