import reflex as rx
from reflex_test.templates import template


def option_1() -> rx.Component:
    return payment_card(
        "Top Up",
        "$5",
        [
            "Use any integrated LLM (GPT, Gemini, Claude, Grok, etc.)",
            "Web search",
            "Enhanced GitHub search",
            "Infinite conversation recall",
            "Customizable workflows",
            "more...",
        ],
    )


def option_2() -> rx.Component:
    return payment_card(
        "Monthly",
        "$10",
        [
            "Everything in Top Up plus...",
            "Priority support",
            "Bonus credits",
            "Early access to new features",
            "more...",
        ],
    )


def option_3() -> rx.Component:
    return payment_card(
        "Business",
        "Contact us",
        [
            "Everything in Monthly plus...",
            "Direct contact with our team",
            "Bespoke workflows",
            "Team knowledge sharing",
            "more...",
        ],
    )


def payment_card(heading: str, price: str, features: list[str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(heading, size="7"),
            rx.heading(price, size="5"),
            rx.divider(width="80%", margin_x="auto"),
            rx.heading("Key features:", size="6"),
            rx.vstack(
                rx.unordered_list(rx.foreach(features, lambda info: rx.list_item(info))),
                width="100%",
                margin_left="1rem",
            ),
            align="center",
        ),
        width="100%",
        # On hover, the background lightness should increase, and the card should grow slightly
        _hover={
            "transform": "scale(1.05)",
            "background": rx.color("gray", 3),
        },
        transition="all 0.1s",
    )


@template(route="/payments_page", title="Payments Page")
def index() -> rx.Component:
    return rx.container(
        rx.heading("Payments Page", size="5"),
        "payments_page",
        rx.hstack(
            option_1(),
            option_2(),
            option_3(),
            align="stretch",
            justify="between",
        ),
    )
