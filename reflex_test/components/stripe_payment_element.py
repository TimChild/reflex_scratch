"""Stripe UI components."""

from typing import Any

import reflex as rx

STRIPE_PUBLIC_KEY = (
    "pk_test_51P5VScRqabseNwj7Bhfkh5uZKkVM5mdD0Cws9vQZvgw5siZMJcjz4h3jGaRrLoVUvzOAtYImuLh6xQqy0nVDMk8o00VyOyGUCc"
)

LOAD_STRIPE_SCRIPT = f"""
const stripePromise = loadStripe('{STRIPE_PUBLIC_KEY}');
"""


class StripeElements(rx.Component):
    """Stripe elements."""

    library = "@stripe/react-stripe-js"
    tag = "Elements"

    options: rx.Var[dict[str, Any]] = {}

    def _get_custom_code(self) -> str | None:
        return super()._get_custom_code() or "" + LOAD_STRIPE_SCRIPT

    def _get_imports(self):
        return rx.utils.imports.merge_imports(  # type: ignore
            super()._get_imports()
            | {
                "@stripe/stripe-js": {rx.vars.ImportVar(tag="loadStripe")},
            }
        )

    def _render(self):
        return (
            super()
            ._render()
            .add_props(
                # Links the externally loaded stripePromise
                stripe=rx.vars.BaseVar(_var_name="stripePromise"),  # type: ignore
            )
        )


class PaymentElement(rx.Component):
    """Stripe payment element component."""

    library = "@stripe/react-stripe-js"
    tag = "PaymentElement"


stripe_elements = StripeElements.create
payment_element = PaymentElement.create
