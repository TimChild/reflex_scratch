import reflex as rx
from pydantic import BaseModel

from reflex_test.templates import template


class ExampleV2Model(BaseModel):
    attr_a: str = "a"
    attr_b: str = "b"


# @rx.serializer
# def serialize_example_v2_model(model: ExampleV2Model) -> dict:
#     print("using specific v2 serializer")
#     return model.model_dump()


@rx.serializer
def serialize_v2_model(model: BaseModel) -> dict:
    print("using general v2 serializer")
    return model.model_dump()


class StateWithV2Model(rx.State):
    regular_var: str = "regular"
    v2_model: ExampleV2Model = ExampleV2Model()


@template(
    route="/pydantic_v2_test",
    title="Pydantic V2 Test",
)
def index() -> rx.Component:
    return rx.container(
        rx.heading("Pydantic V2 Test", size="5"),
        rx.text("This tests whether a pydantic v2 model can be used as a var in a reflex state."),
        rx.card(
            rx.heading("Regular Var", size="4"),
            rx.text(StateWithV2Model.regular_var),
        ),
        rx.card(
            rx.heading("V2 Model", size="4"),
            rx.text(StateWithV2Model.v2_model.attr_a),
            rx.text(StateWithV2Model.v2_model.attr_b),
        ),
    )
