"""
2024-04-25 -- Seems like text_area do not update even when state value updates... Not sure if this is because
I am updating the state values via SyncState of if it's a limitation of text_area.
The data appears on page refresh.

I temporarily saw the same behaviour of text_area not updating, but now I can't reproduce it...

Partially related to caching in redis I think... I was able to get into a state where several things didn't work, but
then after opening a new tab, they started working again (or after changing names of vars)

Then also have to be more careful about setting values on external
states (i.e. can't just update a sub value of an external state)

Main problem is that I forgot to use value=... instead I was putting the value in the children part
"""

import uuid

import reflex as rx

from ..templates import template


class Bar(rx.Base):
    text_value: str = "Some other value"

class TextAreaState(rx.State):
    text_area_value: str = "Initial text area value"
    foo: Bar = Bar()
    bar: Bar = Bar()
    qux: Bar = Bar()

    def update_text_area(self):
        # Works
        self.text_area_value = uuid.uuid4().hex
        self.bar.text_value = uuid.uuid4().hex
        self.qux = Bar(text_value=uuid.uuid4().hex)
        # self.foo.text_value = uuid.uuid4().hex

        # setattr(self, "text_area_value", uuid.uuid4().hex)
        # setattr(self.bar, "text_value", uuid.uuid4().hex)
        # setattr(self, "qux", Bar(text_value=uuid.uuid4().hex))
        setattr(self.foo, "text_value", uuid.uuid4().hex)


class OtherTextAreaState(rx.State):

    @rx.background
    async def update_text_area(self):
        async with self:
            dynamic_state = await self.get_state(TextAreaState)
        # Works
        dynamic_state.text_area_value = uuid.uuid4().hex
        dynamic_state.bar.value = uuid.uuid4().hex
        dynamic_state.qux = Bar(text_value=uuid.uuid4().hex)
        # Doesn't work
        dynamic_state.foo.text_value = uuid.uuid4().hex
        yield



@template(
    route="/dynamic_update_text_area",
    title="dynamic_update_text_area",
)
def index() -> rx.Component:
    return rx.container(
        rx.text("Direct"),
        rx.text_area(value=TextAreaState.text_area_value, read_only=True),
        rx.text("Base var named foo"),
        rx.text_area(value=TextAreaState.foo.text_value, read_only=True),
        rx.text("Base var named bar"),
        rx.text_area(value=TextAreaState.bar.text_value, read_only=True),
        rx.hstack(
            rx.text("update in the same state as value"),
            rx.button("Update text area", on_click=TextAreaState.update_text_area),
        ),
        rx.hstack(
            rx.text("Update from different state"),
            rx.button("Update via different state", on_click=OtherTextAreaState.update_text_area),
        )
    )
