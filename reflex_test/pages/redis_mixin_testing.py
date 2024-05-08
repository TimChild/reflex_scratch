
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
from reflex.state import RouterData

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
    """
    Base mixin for storing data in redis to be shared between states etc. Defaults to per tab storage, but with
    a group_key provided will store data per that group (probably user_id or similar).

    Defaults to storing with a timeout of an hour
    """

    def group_key(self, attr: str) -> str | None:
        """
        Override this method to return a key specific to user to make data available across tabs for that user
        Otherwise will default to using the client_token (per tab)
        """
        return None

    def timeout(self, attr: str) -> int:
        """
        Timeout for the data storage in redis. Override this method to set a different timeout
        """
        return 60*60*1

    def store(self, attr: str, key: str | int, value: model_type):
        """
        Store new value in redis for the attribute and key provided:
        Examples:
            self.key_a = new_key  # To set in current state
            self.store('key_a', self.key_a, a_inst)  # To store the actual value for retrieval by this or other states
        """
        unique_key = self._generate_key(attr, key)
        logger.debug(f'Storing {value} as {unique_key}')
        redis.set(unique_key, dill.dumps(value, byref=True), ex=self.timeout(attr))

    def load(self, attr: str, key: str | int, expected_type: type[model_type] = None, default: model_type | None = None) -> model_type | None:
        """
        Load value from redis for the attribute and key provided:
        Examples:
            a = self.load('key_a', self.key_a, A)  # Provide expected class for validation/type hinting
        """
        unique_key = self._generate_key(attr, key)
        logger.debug(f'Loading {unique_key}')
        data = redis.get(unique_key)
        if data is not None:
            loaded = dill.loads(data)
            logger.debug(f'Loaded {loaded} as {unique_key}')
            if expected_type:
                if not isinstance(loaded, expected_type):
                    raise ValueError(f"Expected {expected_type}, got {type(loaded)}")
            return loaded
        logger.debug(f'No data for key \"{unique_key}\"')
        return default

    def _generate_key(self: Self | rx.State, attr: str, key: str) -> str:
        """Generates a unique key for the data storage in redis"""
        group_key = self.group_key(attr) or self.router.session.client_token
        return f"{group_key}:{self.get_full_name()}:{attr}:{key}"


class ABStorageMixin(StorageBase):
    key_a: int = 0
    key_b: int = 0
    # key_a: str = ''
    # key_b: str = ''



class ProcessA(ABStorageMixin):
    def handle_change_a(self):
        logger.debug('Changing A')
        # new_key = uuid.uuid4().hex[:4]
        new_key = self.key_a + 1
        a = A(
            foo=random.randint(0, 100),
            bar=random.randint(0, 100),
            baz=random.randint(0, 100),
        )
        self.store('key_a', new_key, a)
        self.key_a = new_key

    def handle_change_b(self):
        logger.debug('Changing B')
        # new_key = uuid.uuid4().hex[:4]
        new_key = self.key_b + 1
        b = B(
            fe=random.choice(['fe', 'fi', 'fo', 'fum']),
            fi=random.choice(['fe', 'fi', 'fo', 'fum']),
            fo=random.choice(['fe', 'fi', 'fo', 'fum']),
        )
        self.store('key_b', new_key, b)
        self.key_b = new_key

class ProcessB(ABStorageMixin):
    def update_a(self):
        logger.debug('Updating A')
        a = self.load('key_a', self.key_a, A)
        if a:
            a.foo += 10
            a.bar -= 10
            a.baz *= 2
            self.store('key_a', self.key_a, a)
            # Note: Might at some point be necessary to set a value on self here to trigger updates of cached_vars etc

    def update_b(self):
        logger.debug('Updating B')
        b = self.load('key_b', self.key_b, B)
        if b:
            b.fe = random.choice(['fe', 'fi', 'fo', 'fum'])
            b.fi = random.choice(['fe', 'fi', 'fo', 'fum'])
            b.fo = random.choice(['fe', 'fi', 'fo', 'fum'])
            self.store('key_b', self.key_b, b)


class DisplayA(ProcessA):
    """Anything directly related to what will be displayed to user and user interaction (i.e. including setting the
    on_click for event handlers etc. (but can refer to methods in ProcessBase)"""
    @rx.cached_var
    def a(self) -> str:
        logger.debug('DispA: Getting A')
        loaded = self.load('key_a', self.key_a, A)
        if loaded:
            return loaded.model_dump_json(indent=2)
        return "None"

    @rx.cached_var
    def b(self) -> str:
        logger.debug('DispA: Getting B')
        loaded=self.load('key_b', self.key_b, B)
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
            rx.button('Logs Separator', color_scheme='purple', on_click=cls.log_separator),
        )

    def log_separator(self):
        logger.debug('---' * 20)


class DisplayB(ProcessB, ProcessA):
    @rx.cached_var
    def a(self) -> str:
        logger.debug('DispB: Getting A')
        loaded = self.load('key_a', self.key_a, A)
        if loaded:
            return loaded.model_dump_json(indent=2).upper()
        return "Different"

    @rx.cached_var
    def b(self) -> str:
        logger.debug('DispB: Getting B')
        loaded = self.load('key_b', self.key_b, B)
        if loaded:
            return loaded.model_dump_json(indent=2)*2
        return "Different"

    @classmethod
    def get_component(cls, subheading: str, *args, **kwargs) -> rx.Component:
        return rx.card(
            rx.heading('Alternative View', size='6'),
            rx.heading(subheading, size='4'),
            rx.grid(
                rx.card(rx.text('key_a:')),
                rx.card(rx.text(cls.key_a)),
                rx.card(rx.text('key_b:')),
                rx.card(rx.text(cls.key_b)),
                rows='2', columns='2'

            ),
            rx.grid(
                rx.text('Object of key_a:'),
                rx.text(cls.a),
                rx.text('Object of key_b:'),
                rx.text(cls.b),
                rows='2', columns='2'
            ),
            rx.hstack(
                rx.button('Change A', on_click=cls.handle_change_a),
                rx.button('Change B', on_click=cls.handle_change_b),
                rx.button('Update A', on_click=cls.update_a),
                rx.button('Update B', on_click=cls.update_b),
                wrap='wrap',
            ),
            rx.button('Logs Separator', color_scheme='purple', on_click=cls.log_separator),
        )

    def log_separator(self):
        logger.debug('---' * 20)


class Storage1(ABStorageMixin, rx.State):
    pass

class Storage2(ABStorageMixin, rx.State):
    pass

class A1(DisplayA, Storage1):
    pass

class B1(DisplayB, Storage1):
    pass

class A2(DisplayA, Storage2):
    pass


@template(route='/mixin_with_redis', title='Mixin with Redis')
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading('Mixing together Mixin states', size='5'),
            rx.text(dedent("""
            Working with data that is stored in redis (regular v2 schemas that are serialized/deserialized directly). 
            """)),
            rx.divider(),
            rx.grid(
                A1.get_component('Display A of Storage 1'),
                B1.get_component('Display B of Storage 1'),
                A2.get_component('Display A of Storage 2'),
                columns='3'
            ),
        ),

        padding='2em',
    )