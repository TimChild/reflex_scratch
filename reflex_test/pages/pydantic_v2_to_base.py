from __future__ import annotations

import reflex as rx
from pydantic import BaseModel

from pydantic.v1 import create_model as create_v1_model, Field as V1Field

from ..templates import template


class ReflexCompatibleBaseModel(BaseModel):
    @classmethod
    @property
    def reflex_base_class(cls) -> type[rx.Base]:
        return create_v1_model(
            cls.__name__,
            __base__=rx.Base,
            **{k: V1Field(default=f.default, default_factory=f.default_factory) for k, f in cls.__fields__.items()},
        )

    def to_reflex_base(self) -> rx.Base:
        klass = self.reflex_base_class
        dumped = self.model_dump()
        return klass(
            **{
                k: v.to_reflex_base() if isinstance(v, ReflexCompatibleBaseModel) else v
                for k, v in dumped.items()
                if v is not None
            }
        )

    @classmethod
    def from_reflex_base(cls, reflex_base: rx.Base) -> ReflexCompatibleBaseModel:
        return V2Schema(**reflex_base.dict())


class NestedV2Schema(ReflexCompatibleBaseModel):
    nested_str: str = "nested"


class V2Schema(ReflexCompatibleBaseModel):
    int_val: int = 1
    str_val: str = "hello"
    nested: NestedV2Schema = NestedV2Schema()


class Regular(rx.Base):
    int_val: int = 1
    str_val: str = "hello"


class PydanticPageState(rx.State):
    regular: Regular = Regular()
    v2_schema: V2Schema.reflex_base_class = V2Schema()

    @rx.var
    def custom_str(self) -> str:
        schema = V2Schema.from_reflex_base(self.v2_schema)

        return f"int_val: {schema.int_val}, str_val: {schema.str_val}, nested: {schema.nested.nested_str}"


@template(
    route="/pydantic_v2_to_base",
    title="pydantic_v2_to_base",
)
def index() -> rx.Component:
    return rx.container(
        rx.heading("pydantic_v2_to_base", size="5"),
        rx.divider(),
        rx.text("Regular rx.Base as a var:"),
        rx.text(f"inv_val: {PydanticPageState.regular.int_val}, str_val: {PydanticPageState.regular.str_val}"),
        rx.divider(),
        rx.text("Converted from pydantic v2 to rx.Base:"),
        rx.text(
            f"int_val: {PydanticPageState.v2_schema.int_val}, str_val: {PydanticPageState.v2_schema.str_val}, nested: {PydanticPageState.v2_schema.nested.nested_str}"
        ),
        rx.text("Custom str var:"),
        rx.text(PydanticPageState.custom_str),
    )
