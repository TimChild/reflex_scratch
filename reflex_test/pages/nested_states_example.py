from typing import cast, Callable, ClassVar, Union

import reflex as rx

from reflex_test.templates import template


class A(rx.ComponentState):
    fixed_val: ClassVar[int] = 0
    val_a: int = 1

    @classmethod  # <<< By the way, if this is missing, the compilation error is pretty cryptic
    def get_component(
        cls,
        index_: int,
        *args,
        handle_submission: Union[Callable, None] = None,
        default_val: int = None,
        fixed_val: int = None,
        **kwargs,
    ):
        # It's pretty easy to use handlers from Higher level components in the layout of this component
        additional_button = (
            rx.button("Trigger the HighLevelSubmission", on_click=handle_submission)
            if handle_submission
            else rx.fragment()
        )

        if fixed_val:
            cls.fixed_val = fixed_val  # <<< This is a way to set a value on the class that is fixed

        # This would also be nice to be able to do (currently it makes the value fixed)
        if default_val:
            cls.val_a = default_val

        return rx.card(
            rx.text(f"A: {index_}"),
            rx.text(f"val_a: {cls.val_a}, fixed_val: {cls.fixed_val}"),
            rx.button("Increment", on_click=cls.increment),
            rx.button("Decrement", on_click=cls.decrement),
            additional_button,
        )

    def increment(self):
        self.val_a += 1

    def decrement(self):
        self.val_a -= 1


class B(rx.ComponentState):
    val_b: int = 2
    complicated_value: int = 0

    # <<< Ideally this would reference the val_a from the associated A component
    val_a_reference: int = None
    state_a: ClassVar[type[rx.State]] = (
        # <<< Or at least this could hold a reference to the state class that the value comes from.
        None
    )

    @classmethod
    def get_component(cls, index: int, val_a: int | rx.Var[int], state_a: type[rx.State], *args, **kwargs):
        # I thought I'd be able to pass in the `state_a` here and then be able to use it in event handler methods
        # somehow, but I don't see the clean way to do it...

        # I thought something like this might work... I think it could be done in the .create() method?
        cls.state_a = state_a

        # This would be ideal, but I don't think there is any easy way to make this work
        # cls.val_a_reference = val_a

        return rx.card(
            rx.text(f"B: {index}"),
            rx.text(
                "Imagine this one needs to know the value of an A component to work. "
                "It's easy to use the A.val_a in the layout of this component",
                weight="bold",
            ),
            rx.text(f"val_b: {cls.val_b}"),
            rx.text(f"val_a + val_b: {val_a + cls.val_b}"),
            rx.button("Increment", on_click=cls.increment),
            rx.button("Decrement", on_click=cls.decrement),
            rx.divider(),
            rx.text("But I'm not sure how I could use that in a calculated var or event handler", weight="bold"),
            # rx.text(f'Result of a cached_var that uses val_a and cls.val_b: {cls.cached_example}'),
            rx.button("Do something complicated with val_a and val_b", on_click=cls.do_complicated_stuff),
            rx.text(f"complicated_value: {cls.complicated_value}"),
        )

    @classmethod
    def create(cls, index, val_a, state_a, *children, **props) -> "rx.Component":
        # Copied from rx.ComponentState.create
        cls._per_component_state_instance_count += 1
        state_cls_name = f"{cls.__name__}_n{cls._per_component_state_instance_count}"
        component_state = type(state_cls_name, (cls, rx.State), {}, mixin=False)
        component = component_state.get_component(index, val_a, state_a, *children, **props)
        component.State = component_state
        ####

        # # I thought I'd be able to set values on the dynamically created class here at least...
        # component_state.state_a = state_a  # I thought this would work, but it doesn't
        # component_state.val_a_reference = val_a  # This would be nice, but I don't expect it to be possible
        return component

    def increment(self):
        self.val_b += 1

    def decrement(self):
        self.val_b -= 1

    # @rx.cached_var
    # def cached_example(self):
    #     # Can't use get_state because cached_var can't be an async function because it's a property under the hood
    #     # Pretty sure this is just not possible...
    #     val_a = self.val_a_reference  # This would be nice, but I don't expect it to be possible
    #     return self.val_b ** self.val_a_reference

    async def do_complicated_stuff(self):
        """
        Real example might be that the options in B need to be loaded from a database based on a selection (in this case
         from an A component).
        Other than that, A and B are separate, and the selection that B depends on could come from a different
        place altogether if used in a different page for example.
        """
        # val_a = self.val_a_reference  # This would be nice, but I don't expect it to be possible

        # Thought about trying to get the whole state
        val_a = cast(A, await self.get_state(self.state_a)).val_a
        # But get an AttributeError: NoneType object has no attribute `get_full_name`
        # placeholder for something that would actually require server-side
        self.complicated_value = self.val_b**val_a


class HighLevelState(rx.State):
    main_result: int = 0

    async def handle_submission(self):
        # Collect the values from the relevant component states
        # (where I have those states organized in the States class)
        # In this HighLevelState I can just target the specific states I need which works well
        state_a = cast(A, await self.get_state(StatesAndComponents.a.State))
        state_b = cast(B, await self.get_state(StatesAndComponents.b.State))
        state_a_2 = cast(A, await self.get_state(StatesAndComponents.a_2.State))
        state_b_2 = cast(B, await self.get_state(StatesAndComponents.b_2.State))

        # Placeholder for something that would actually require server-side
        self.main_result = state_a.val_a + state_b.val_b + state_a_2.val_a + state_b_2.val_b


class StatesAndComponents:
    """
    Currently, I just use a class to hold all the State and ComponentState objects together.

    This is useful if I want to access states from this page in another page, then I know I only have to look in this
    class. And I can quickly and easily see if I am using States from other places here too.
    """

    high_level = HighLevelState

    a = A.create(1, fixed_val=10)
    b = B.create(1, a.State.val_a, a.State)
    a_2 = A.create(2, handle_submission=high_level.handle_submission, fixed_val=20)
    b_2 = B.create(2, a_2.State.val_a, a_2.State)
    # ^^^ This works pretty well as long as the dependency is one directional

    a_3 = A.create(3, default_val=100)


@template(route="/passing_states_between_components", title="Passing States between Components Example")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Nested States Example", size="5"),
            rx.divider(),
            rx.text(
                "I have several groups of components that are almost standalone and work nicely with ComponentState",
                weight="bold",
            ),
            rx.grid(
                StatesAndComponents.a,
                StatesAndComponents.b,
                StatesAndComponents.a_2,
                StatesAndComponents.b_2,
                columns="2",
                rows="2",
            ),
            rx.divider(),
            rx.text("Then I have some higher level states that use values from those components", weight="bold"),
            rx.button("Main submission", on_click=StatesAndComponents.high_level.handle_submission),
            rx.card(
                rx.text("Main output"),
                rx.divider(),
                rx.text("The main result from the HighLevelState (adding all 4 values together is):", weight="bold"),
                rx.text(StatesAndComponents.high_level.main_result),
            ),
            rx.divider(),
            rx.text(
                "It would also be nice to be able to set the initial values in a ComponentState via the create method."
                " But the way I've implemented it here ends up making the value fixed."
            ),
            StatesAndComponents.a_3,
        ),
        padding="2em",
    )
