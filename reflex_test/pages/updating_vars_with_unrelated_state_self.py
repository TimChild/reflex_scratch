import asyncio

import reflex as rx

from reflex_test.templates import template


class SomeVars(rx.Base):
    var1: int = 1
    var2: int = 2


class OtherVars(rx.Base):
    other1: int = 3
    other2: int = 4


class StateWithVars(rx.State):
    some_vars: SomeVars = SomeVars()
    other_vars: OtherVars = OtherVars()


class UnrelatedState(rx.State):
    unrelated_var: int = 5

    @rx.event(background=True)
    async def do_stuff_background(self):
        async with self:
            s = await self.get_state(StateWithVars)
            some_vars = s.some_vars
            some_vars.var1 += 1
            var2 = some_vars.var2
        yield rx.toast(
            "Updated some_vars.var1 directly after getting state and saved some_vars.var2 as var2", duration=2000
        )
        await asyncio.sleep(1)
        async with self:
            some_vars.var1 -= 1
            var2 += 1
        yield rx.toast(
            "Updated some_vars.var1 and var2 without getting from state again (only the some_vars.var1 updates though)",
            duration=2000,
        )
        await asyncio.sleep(1)
        async with self:
            s = await self.get_state(StateWithVars)
            some_vars = s.some_vars
            some_vars.var2 += 1
            self.unrelated_var += 1
        yield rx.toast("Updated var2 after getting related state again", duration=2000)


@template(route="/updating_vars_with_unrelated_state_self", title="Updating Vars with Unrelated State Self")
def index() -> rx.Component:
    return rx.container(
        rx.heading("Updating Vars with Unrelated State Self", size="5"),
        rx.card(
            rx.heading("Some Vars", size="4"),
            rx.text(StateWithVars.some_vars.var1),
            rx.text(StateWithVars.some_vars.var2),
        ),
        rx.card(
            rx.heading("Other Vars", size="4"),
            rx.text(StateWithVars.other_vars.other1),
            rx.text(StateWithVars.other_vars.other2),
        ),
        rx.card(
            rx.heading("Unrelated State", size="4"),
            rx.text(UnrelatedState.unrelated_var),
        ),
        rx.button("Do Stuff Background", on_click=UnrelatedState.do_stuff_background),
    )
