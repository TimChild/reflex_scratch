"""Common templates used between pages in the app."""

from __future__ import annotations

from reflex_test import styles
from typing import Callable

import reflex as rx

# Meta tags for the app.
default_meta = [
    {
        "name": "viewport",
        "content": "width=device-width, shrink-to-fit=no, initial-scale=1",
    },
]


def menu_item_link(text, href):
    return rx.menu.item(
        rx.link(
            text,
            href=href,
            width="100%",
            color="inherit",
        ),
        _hover={
            "color": styles.accent_color,
            "background_color": styles.accent_text_color,
        },
    )


def menu_button() -> rx.Component:
    """The menu button on the top right of the page.

    Returns:
        The menu button component.
    """
    from reflex.page import get_decorated_pages

    return rx.box(
        rx.menu.root(
            rx.menu.trigger(
                rx.icon(
                    "menu",
                    size=36,
                    color=styles.accent_text_color,
                ),
                background_color=styles.accent_color,
            ),
            rx.menu.content(
                *[menu_item_link(page["title"], page["route"]) for page in get_decorated_pages()],
                rx.menu.separator(),
                menu_item_link("Logout", "/logout"),
            ),
        ),
        position="fixed",
        right="1.5em",
        top="1.5em",
        z_index="500",
    )


def nav_bar() -> rx.Component:
    """The navigation bar for the app.

    Returns:
        The navigation bar component.
    """
    return rx.hstack(
        rx.link(
            "Athena",
            href="/",
            font_size="1.5em",
            color=styles.accent_text_color,
            margin="0.5em 1em",
        ),
        menu_button(),
    )


class ThemeState(rx.State):
    """The state for the theme of the app."""

    accent_color: str = "indigo"


def template(
    route: str | None = None,
    title: str | None = None,
    image: str | None = None,
    description: str | None = None,
    meta: str | None = None,
    script_tags: list[rx.Component] | None = None,
    on_load: rx.event.EventHandler | list[rx.event.EventHandler] | None = None,
) -> Callable[[Callable[[], rx.Component]], rx.Component]:
    """The template for each page of the app.

    Args:
        route: The route to reach the page.
        title: The title of the page.
        image: The favicon of the page.
        description: The description of the page.
        meta: Additionnal meta to add to the page.
        on_load: The event handler(s) called when the page load.
        script_tags: Scripts to attach to the page.

    Returns:
        The template with the page content.
    """

    def decorator(page_content: Callable[[], rx.Component]) -> rx.Component:
        """The template for each page of the app.

        Args:
            page_content: The content of the page.

        Returns:
            The template with the page content.
        """
        # Get the meta tags for the page.
        all_meta = [*default_meta, *(meta or [])]

        def templated_page():
            return rx.vstack(
                nav_bar(),
                rx.container(
                    # sidebar(),
                    rx.box(
                        rx.box(
                            page_content(),
                            **styles.template_content_style,
                        ),
                        **styles.template_page_style,
                    ),
                    width=styles.content_width_vw,
                    size="4",
                ),
            )

        @rx.page(
            route=route,
            title=title,
            image=image,
            description=description,
            meta=all_meta,
            script_tags=script_tags,
            on_load=on_load,
        )
        def theme_wrap():
            return rx.theme(
                templated_page(),
                accent_color=ThemeState.accent_color,
            )

        return theme_wrap

    return decorator
