import uuid
from typing import ClassVar, Self

import reflex as rx

from reflex_test.templates import template


class StatefulComponentBase(rx.State, mixin=True):
    _unique_int: ClassVar[int] = 0  # Just so class names don't end up super long
    _instance_mapping: ClassVar[dict[str, Self]] = {}

    @classmethod
    def get_class(cls, uid: str) -> Self:
        """Use this to access values from otherwise standalone component"""
        uid = str(uid)
        if uid in cls._instance_mapping:
            return cls._instance_mapping[uid]

        # Create a new type with a unique name inhering from this cls and rx.State as bases
        cls._unique_int += 1
        # unique_cls: type = type(f"{cls.__name__}_{cls._unique_int}", (cls, rx.State), {})
        unique_cls: type = type(f"{cls.__name__}_{cls._unique_int}", (cls,), {})
        cls._instance_mapping[uid] = unique_cls
        return unique_cls

    @classmethod
    def create(cls, *args, uid: str = None, **kwargs) -> rx.Component:
        """Creates component but with a unique class name each time to prevent state conflicts"""
        uid = str(uid) if uid else str(uuid.uuid4())
        klass = cls.get_class(uid)
        return klass.component(*args, **kwargs)

    @classmethod
    def component(cls, *args, **kwargs) -> rx.Component:
        """This method must be implemented in the subclass to return a component (taking any args and kwargs)"""
        raise NotImplementedError("Must implement component method in subclass")


class ExampleComponent(StatefulComponentBase):
    value: int = 0

    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1

    @classmethod
    def component(cls) -> rx.Component:
        return rx.card(
            rx.heading("Example Component", size="2"),
            rx.text(f"Selected value is: {cls.value}"),
            rx.hstack(
                rx.button("Increment", on_click=cls.increment, color_scheme="green"),
                rx.button("Decrement", on_click=cls.decrement, color_scheme="red"),
            ),
        )


example_component = ExampleComponent.create


def my_stateful_component_mixin_layout() -> rx.Component:
    return rx.vstack(
        rx.heading("Stateful Unique Components", size="5"),
        rx.divider(),
        rx.hstack(
            example_component(uid="1"),
            example_component(uid="2"),
            example_component(uid="3"),
        ),
        rx.divider(),
        rx.heading("Accessing values from the components with provided uid", size="3"),
        rx.hstack(
            rx.card(rx.text(f"{ExampleComponent.get_class('1').value}", weight="bold")),
            rx.card(rx.text(f"{ExampleComponent.get_class('2').value}", weight="bold")),
            rx.card(rx.text(f"{ExampleComponent.get_class('3').value}", weight="bold")),
        ),
        rx.divider(),
        rx.heading("Can also just create standalone components", size="3"),
        example_component(),
        example_component(),
    )


class ComponentA(rx.ComponentState):
    var_a: int = 0

    @classmethod
    def get_component(cls, *children, **props) -> rx.Component:
        return rx.card(
            rx.heading("Component A", size="2"),
            rx.text(f"Var A: {cls.var_a}"),
            rx.button("Increment", on_click=cls.increment, color_scheme="green"),
            rx.button("Decrement", on_click=cls.decrement, color_scheme="red"),
        )

    def increment(self):
        self.var_a += 1

    def decrement(self):
        self.var_a -= 1


class StateThatGetsFromComponent(rx.State):
    value_from_example: int = 0
    value_from_component_a: int = 0

    async def refresh(self):
        # With my mixin, I could use knowledge of the specific uid to get the state wherever I want
        example = await self.get_state(ExampleComponent.get_class("example_a_id"))
        self.value_from_example = example.value

        # With the built in rx.ComponentState, it relies on getting the object that was created...
        component_a = await self.get_state(StatefulComponents.a_1.State)
        self.value_from_component_a = component_a.var_a


class StatefulComponents:
    # Create all Stateful Component objects somewhere that can be accessed anywhere it is needed (i.e. in page for
    # layout, or in an event handler to extract data from state)
    # Note: This should be imported locally if in a state outside of the page (although that probably shouldn't be
    # done anyway). Imports go Component > State > Page.
    a_1: ComponentA = ComponentA.create()


@template(route="/stateful_component_mixin", title="Stateful Unique Components")
def index() -> rx.Component:
    a_1 = StatefulComponents.a_1
    a_2 = ComponentA.create()

    return rx.container(
        rx.spacer(height="5em"),
        my_stateful_component_mixin_layout(),
        rx.divider(),
        a_1,
        a_2,
        rx.text(f"Value in A1: {a_1.State.var_a}"),
        rx.text(f"Value in A2: {a_2.State.var_a}"),
        rx.divider(),
        rx.heading("State that gets from component", size="3"),
        ExampleComponent.create(uid="example_a_id"),
        rx.text(f"Getting from my mixin {StateThatGetsFromComponent.value_from_example}"),
        rx.text(f"Getting from rx.ComponentState {StateThatGetsFromComponent.value_from_component_a}"),
        rx.button("Refresh", on_click=StateThatGetsFromComponent.refresh),
    )
