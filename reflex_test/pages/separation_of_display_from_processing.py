
from __future__ import annotations

import logging
import abc
import random
import uuid
from textwrap import dedent
from typing import TypeVar, TYPE_CHECKING, Self, Protocol

import dill
from fakeredis import FakeRedis

import reflex as rx
from pydantic import BaseModel

from reflex_test.templates import template

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


if TYPE_CHECKING:
    Base = object
else:
    Base = rx.Base


database: dict[int, Data] = {}

def process(input_a: str):
    global database
    # Stand in for an async processing function that stores result in db and returns only the id
    data = Data(attr_a=input_a.title(), attr_b=input_a.upper())
    next_id = len(database)
    database[next_id] = data
    return next_id

class Data(BaseModel):
    attr_a: str
    attr_b: str


def load_data(data_id: int) -> Data:
    global database
    # Stand in for an async load from db function
    return database.get(data_id, Data(attr_a='', attr_b=''))

class UpdatesMixin(Base):
    async def updates(self):
        classes_to_update = [
            DisplayStuff,
        ]
        for c in classes_to_update:
            state = await self.get_state(c)
            async for e in state.update():
                yield e

class DoStuffState(UpdatesMixin, rx.State):
    a_id: int = 0
    b_id: int = 0

    async def do_stuff(self, data: dict[str, str]):
        self.a_id = process(data['input_a'])
        self.b_id = process(data['input_b'])

        async for e in self.updates():
            yield e



class DisplayStuff(rx.State):
    # Not inheriting from DoStuffState because this state may need to load a lot of data, but the DoStuffState only
    # needs to store ids or keys
    attr_a: str = ""
    attr_b: str = ""

    async def update(self):
        doer = await self.get_state(DoStuffState)
        data_a = load_data(doer.a_id)
        logger.debug(f'Updating DisplayStuff with Data: {data_a}')
        self.attr_a = data_a.attr_a
        self.attr_b = data_a.attr_b
        yield

    @classmethod
    def get_component(cls, title: str) -> rx.Component:
        return rx.card(
            rx.heading(title),
            rx.text(f'Attribute A: {cls.attr_a}'),
            rx.text(f'Attribute B: {cls.attr_b}'),
        )




@template(route='/separation_of_processing_and_display', title='Separation of processing and display')
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading('Separation of processing and display', size='5'),
            rx.markdown(dedent("""
            Overall aim is to make it easier to separate the code related to event handling and processing of data from
            the displaying of that data.

            The specific case in mind is with the agent runner, where the processing is general whether carried out in
            full by a submit on the main app, or in partial steps in the chain builder etc.
            Display wise, there are three different views of the data; the main app where just the streaming messages
            and minimal other info is required, the run info page which should show lots of information, and the
            chain builder page which is more similar to the main app display but may include some additional things as
            well.
            
            For all of the processing, it's not necessary to store much in the State at all, can just store 
            db ids or redis keys and load/save those when needed in the processing functions. This also has the benefit
            of not having to worry about any serialization or compatability issues with storing v2 pydantic models for 
            example. 

            For now I think it make sense that they all share the same processing state (i.e. navigating from app page
            to chain builder or run info, the same conversation should be displayed). But I'm not sure how to
            efficiently handle displaying the information in the different ways...

            On the one hand, the separate displays can all chose how to show information from the same state in
            different ways, but **only** if that information is stored in the state already. 
            Additional data can be loaded based on database/redis keys, but then do I store that data back into the
            same shared state that the others use?
            """)),
            rx.divider(),
            rx.card(
              rx.heading('DoStuff stuff'),
                rx.form(
                    rx.input(name='input_a', placeholder='Input A'),
                    rx.input(name='input_b', placeholder='Input B'),
                    rx.button('Do Stuff'),
                    on_submit=DoStuffState.do_stuff,
                ),
                rx.text(f'State values: {DoStuffState.a_id}, {DoStuffState.b_id}')
            ),
            rx.grid(
                DisplayStuff.get_component('Display A'),
                columns='3'
            ),
        ),

        padding='2em',
    )