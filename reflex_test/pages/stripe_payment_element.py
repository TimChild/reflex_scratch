"""The payment page."""

import reflex as rx
import stripe

from ..components.stripe_payment_element import payment_element, stripe_elements
from ..templates import template

STRIPE_SECRET_KEY = (
    "sk_test_51P5VScRqabseNwj7yyzulqSLi2qnargWEpmePpLm2JkIimG3IxKafplNoehrijgp4jgEiama7JKUWHdLL6toHwQF00QIYAeyuT"
)
stripe.api_key = STRIPE_SECRET_KEY


# RETURN_URL_BASE = f"http://localhost:8000"  # or 3000?

# temp_session = stripe.PaymentIntent.create(
#     amount=1000,
#     currency="usd",
#     payment_method_types=["card"],
#     payment_method="pm_card_visa",
#     confirm=True,
#     # return_url=f"{RETURN_URL_BASE}/payment?session_id={CHECKOUT_SESSION_ID}",
# )


class PaymentState(rx.State):
    """The payment page state."""

    # Amount in cents
    amount: float = 1000

    # _checkout_session: stripe.checkout.Session = stripe.checkout.Session.create()

    @rx.var
    def client_secret(self) -> str:
        """The client secret for the payment intent."""
        session = stripe.PaymentIntent.create(
            amount=self.amount,
            currency="usd",
            payment_method_types=["card"],
            payment_method="pm_card_visa",
            confirm=True,
            # return_url=f"{RETURN_URL_BASE}/payment?session_id={CHECKOUT_SESSION_ID}",
        )
        return session.client_secret or ""


@template(route="/payment", title="Purchase Credits", description="Credit purchase page")
def index() -> rx.Component:
    """The payment page."""
    return rx.container(
        rx.vstack(
            rx.heading("Purchase additional credits", size="5"),
            rx.card(
                stripe_elements(
                    rx.form(
                        rx.vstack(
                            payment_element(),
                            rx.button("Submit", width="100%"),
                        )
                    ),
                    options=dict(
                        clientSecret=PaymentState.client_secret,
                        # clientSecret=temp_session.client_secret,
                        appearance={"theme": "night"},
                    ),
                ),
                spacing="2",
            ),
        ),
    )
