
from __future__ import annotations

import logging

import reflex as rx
from pydantic import BaseModel

from reflex_test.templates import template

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Data(BaseModel):
    attr_a: str
    attr_b: str

database: dict[int, Data] = {}

def load_data(data_id: int) -> Data:
    # Stand in for an async load from db function
    return database.get(data_id, Data(attr_a='', attr_b=''))

def process(input_a: str):
    # Stand in for an async processing function that stores result in db and returns only the id
    data = Data(attr_a=input_a.title(), attr_b=input_a.upper())
    next_id = len(database)
    database[next_id] = data
    return next_id


class HandlerState(rx.State):
    input_a: str

    data_id: int

    async def do_stuff_on_click(self):
        # Some process that stores result in redis/database
        data_id = process(self.input_a)
        # Only store the id here to avoid storing whole object in state and serialization issues
        self.data_id = data_id


class DisplayMixin(rx.Base):
    @rx.cached_var
    def data_a_cached(self) -> str:
        data = load_data(self.data_id)
        return data.attr_a

    @rx.cached_var
    def data_b_cached(self) -> str:
        data = load_data(self.data_id)
        return data.attr_b


class DisplayState(DisplayMixin, HandlerState):
    pass


class AlternativeDisplayMixin(rx.Base):
    data_attr_a: str = ""
    data_attr_b: str = ""

    async def update_display_info(self):
        data = load_data(self.data_id)
        self.data_attr_a = f'Attribute A: {data.attr_a}'
        self.data_attr_b = f'Attribute B: {data.attr_b}'

class AlternativeDisplayState(AlternativeDisplayMixin, HandlerState):
    pass


@template(route='/async_cached_var_issues', title='Async Cached Var Issues')
def index() -> rx.Component:
    return rx.container(
        rx.card(
            rx.heading('Handler stuff', size='5'),
            rx.input(value=HandlerState.input_a, label='Input A', on_change=HandlerState.set_input_a),
            rx.button('Do Stuff', on_click=HandlerState.do_stuff_on_click),
        ),
        rx.hstack(
            rx.card(
                rx.heading('Display data via cached_vars', size='5'),
                rx.markdown(f'{DisplayState.data_a_cached}\n\n{DisplayState.data_b_cached}'),
            ),
            rx.card(
                rx.heading('Alternative Display of data', size='5'),
                rx.markdown(f'{AlternativeDisplayState.data_attr_a}\n\n{AlternativeDisplayState.data_attr_b}'),
                rx.button('Update Display Info', on_click=AlternativeDisplayState.update_display_info),
            )
        ),
    )


