
from __future__ import annotations

import logging
import abc
import random
import uuid
from textwrap import dedent
from typing import TypeVar, TYPE_CHECKING

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

model_type = TypeVar('model_type', bound=BaseModel)

redis = FakeRedis(decode_responses=False)

class A(BaseModel):
    foo: int = 0
    bar: int = 10
    baz: int = 20


class B(BaseModel):
    fe: str = "fe"
    fi: str = "fi"
    fo: str = "fo"


class StorageBase(Base):

    def _generate_key(self, key: str) -> str:
        return f"{self.__class__.__name__}_{key}"

    def store(self, key: str, value: model_type):
        redis.set(self._generate_key(key), dill.dumps(value, byref=True), ex=60)
        logger.debug(f'Stored {value} as {self._generate_key(key)}')

    def load(self, key: str, expected_type: type[model_type] = None, allow_none: bool = True) -> model_type | None:
        data = redis.get(self._generate_key(key))
        if data is not None:
            loaded = dill.loads(data)
            logger.debug(f'Loaded {loaded} as {self._generate_key(key)}')
            if expected_type:
                if not isinstance(loaded, expected_type):
                    raise ValueError(f"Expected {expected_type}, got {type(loaded)}")
            return loaded
        if not allow_none:
            raise ValueError(f"Data for {key} is None")
        logger.debug(f'No data for {key}')
        return None

class DisplayBase(Base):

    @classmethod
    @abc.abstractmethod
    def get_component(cls, *args, **kwargs) -> rx.Component:
        pass

class ProcessBase(Base):
    pass


class ConcreteStorage(StorageBase):
    key_a: str = ''
    key_b: str = ''


class ConcreteProcess(ProcessBase, ConcreteStorage):
    def handle_change_a(self):
        logger.debug(f'Changing A')
        new_key = uuid.uuid4().hex[:4]
        a = A(
            foo=random.randint(0, 100),
            bar=random.randint(0, 100),
            baz=random.randint(0, 100),
        )
        self.store(new_key, a)
        self.key_a = new_key

    def handle_change_b(self):
        logger.debug(f'Changing B')
        new_key = uuid.uuid4().hex[:4]
        b = B(
            fe=random.choice(['fe', 'fi', 'fo', 'fum']),
            fi=random.choice(['fe', 'fi', 'fo', 'fum']),
            fo=random.choice(['fe', 'fi', 'fo', 'fum']),
        )
        self.store(new_key, b)
        self.key_b = new_key


class ConcreteDisplay(DisplayBase, ConcreteProcess):
    """Anything directly related to what will be displayed to user and user interaction (i.e. including setting the
    on_click for event handlers etc (but can refer to methods in ProcessBase)"""
    @rx.cached_var
    def a(self) -> str:
        loaded = self.load(self.key_a, A)
        if loaded:
            return loaded.model_dump_json(indent=2)
        return "None"

    @rx.cached_var
    def b(self) -> str:
        loaded=self.load(self.key_b, B)
        if loaded:
            return loaded.model_dump_json(indent=2)
        return "None"

    @classmethod
    def get_component(cls, subheading: str, *args, **kwargs) -> rx.Component:
        return rx.card(
            rx.heading('Combined display for A and B', size='6'),
            rx.heading(subheading, size='4'),
            rx.text('Displaying the values'),
            rx.text(f'Value of key_a: {cls.key_a}'),
            rx.text(f'Value of key_b: {cls.key_b}'),
            rx.text('Object of key_a:'),
            rx.text(cls.a),
            rx.text('Object of key_b:'),
            rx.text(cls.b),
            rx.hstack(
                rx.button('Change A', on_click=cls.handle_change_a),
                rx.button('Change B', on_click=cls.handle_change_b),
            ),
        )


class DifferentDisplay(DisplayBase, ConcreteProcess):
    @rx.cached_var
    def a(self) -> str:
        loaded = self.load(self.key_a, A)
        if loaded:
            return loaded.model_dump_json(indent=2).upper()
        return "Different"

    @rx.cached_var
    def b(self) -> str:
        return 'always b'

    @classmethod
    def get_component(cls, subheading: str, *args, **kwargs) -> rx.Component:
        return rx.card(
            rx.heading('Combined display for A and B', size='6'),
            rx.heading(subheading, size='4'),
            rx.text('Displaying the values'),
            rx.text(f'Value of key_a: {cls.key_a}'),
            rx.text(f'Value of key_b: {cls.key_b}'),
            rx.text('Object of key_a:'),
            rx.text(cls.a),
            rx.text('Object of key_b:'),
            rx.text(cls.b),
            rx.hstack(
                rx.button('Change A', on_click=cls.handle_change_a),
                rx.button('Change B', on_click=cls.handle_change_b),
            ),
        )




class CompleteState(ConcreteDisplay, rx.State):
    pass

class CompleteState2(ConcreteDisplay, rx.State):
    pass


class CompleteState3(DifferentDisplay, rx.State):
    pass

@template(route='/using_values_in_rxBase', title='Using values in rxBase')
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading('Mixing together Mixin states', size='5'),
            rx.text(dedent("""
            Working with data that is stored in redis (regular v2 schemas that are serialized/deserialized directly). 
            """)),
            rx.divider(),
            rx.hstack(
                CompleteState.get_component('First Complete State'),
                CompleteState2.get_component('Second Complete State'),
                CompleteState3.get_component('Different State'),
            ),
        ),

        padding='2em',
    )