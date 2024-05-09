from __future__ import annotations

import logging
import random
from textwrap import dedent
from typing import TYPE_CHECKING, ClassVar, Callable, TypeVar, Generic, cast

import reflex as rx
from pydantic import BaseModel

from reflex_test.templates import template

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if TYPE_CHECKING:
    Base = object
else:
    Base = rx.Base

database: dict[int, DataA] = {}


async def save_data(data: BaseModel) -> int:
    global database
    # Stand in for an async save to db function
    next_id = len(database)
    database[next_id] = data
    return next_id


async def load_data(data_id: int) -> BaseModel | None:
    global database
    # Stand in for an async load from db function
    return database.get(data_id, None)


class BackendVarsBase(Base):
    async def store(self, *args, **kwargs):
        raise NotImplementedError

    async def load(self, *args, **kwargs):
        raise NotImplementedError


class FrontendVarsBase(Base):
    def update(self, *args, **kwargs):
        raise NotImplementedError


frontend_type = TypeVar("frontend_type", bound=FrontendVarsBase)
backend_type = TypeVar("backend_type", bound=BackendVarsBase)


class ControllerBase(Generic[frontend_type, backend_type]):
    linked_states: dict[str, set[FrontendVarsBase | type[rx.State]]] = {}

    @classmethod
    def register(cls, backend_state: backend_type | type[rx.State], frontend_state: frontend_type | type[rx.State]):
        cls.linked_states.setdefault(backend_state.get_full_name(), set()).add(frontend_state)

    def __init__(
        self,
        self_state: rx.State | rx.ComponentState,
        backend_state_class: type[rx.State],
        sync_key: str = None,
        user=None,
    ):
        self.self_state = self_state
        self._backend_state_class = backend_state_class
        self._bvars = None
        self.sync_key = sync_key
        self.user = user

    async def get_bvars(self, refresh: bool = False) -> backend_type:
        if self._bvars is None or refresh:
            self._bvars = await self.self_state.get_state(self._backend_state_class)
        return self._bvars

    async def update_frontend(self, **kwargs):
        bvars = await self.get_bvars()
        for fvar_class in self.linked_states.get(bvars.get_full_name(), []):
            fvars = cast(FrontendVarsBase, await self.self_state.get_state(fvar_class))
            fvars.update(**kwargs)


NOT_SET = object()


class DataA(BaseModel):
    foo: int = 0
    bar: int = 0
    baz: int = 0


class DataB(BaseModel):
    fe: str = ""
    fi: str = ""
    fo: str = ""


DataType = TypeVar("DataType", DataA, DataB)


class BackendVars(BackendVarsBase):
    a_id: int = 0
    b_id: int = 0

    async def store(self, data_a: DataA = NOT_SET, data_b: DataB = NOT_SET):
        if data_a is not NOT_SET:
            self.a_id = await save_data(data_a)
        if data_b is not NOT_SET:
            self.b_id = await save_data(data_b)

    async def load(self, data_type: type[DataType]) -> DataType:
        if data_type == DataA:
            return await load_data(self.a_id)
        elif data_type == DataB:
            return await load_data(self.b_id)
        else:
            raise ValueError(f"Invalid data type {data_type}")


class FrontendVarsA(FrontendVarsBase):
    # Stand in for basic display of data (e.g. main app)
    a_id_copy: int = 0
    b_id_copy: int = 0
    a_repr: str = ""
    b_repr: str = ""

    def update(self, data_a: DataA = NOT_SET, data_b: DataB = NOT_SET, a_id: int = NOT_SET, b_id: int = NOT_SET):
        if data_a is not NOT_SET:
            self.a_repr = str(data_a)
        if data_b is not NOT_SET:
            self.b_repr = str(data_b)
        if a_id is not NOT_SET:
            self.a_id_copy = a_id
        if b_id is not NOT_SET:
            self.b_id_copy = b_id


def display_type_A(
    fvars: FrontendVarsA | type[rx.State], title: str, on_click_a: Callable, on_click_b: Callable
) -> rx.Component:
    return rx.card(
        rx.heading(title, size="6"),
        rx.heading("Combined view of Data A and B", size="4"),
        rx.text(f"A id: {fvars.a_id_copy}"),
        rx.text(f"B id: {fvars.b_id_copy}"),
        rx.text(f"Attribute A: {fvars.a_repr}"),
        rx.text(f"Attribute B: {fvars.b_repr}"),
        rx.hstack(
            rx.button("Change A", on_click=on_click_a),
            rx.button("Change B", on_click=on_click_b),
        ),
    )


class FrontendVarsB(FrontendVarsBase):
    # Stand in for a much more comprehensive display of data (e.g. run info)
    a_id_copy: int = 0
    b_id_copy: int = 0
    combined_as: str = ""
    combined_bs: str = ""

    def update(self, data_a: DataA = NOT_SET, data_b: DataB = NOT_SET, a_id: int = NOT_SET, b_id: int = NOT_SET):
        if data_a is not NOT_SET:
            self.combined_as = f"<{data_a.foo}, {data_a.bar}, {data_a.baz}>"
        if data_b is not NOT_SET:
            self.combined_bs = f"<{data_b.fe}, {data_b.fi}, {data_b.fo}>"
        if a_id is not NOT_SET:
            self.a_id_copy = a_id
        if b_id is not NOT_SET:
            self.b_id_copy = b_id


def display_type_B(
    fvars: FrontendVarsB | type[rx.State],
    title: str,
    on_click_change_a: Callable,
    on_click_change_b: Callable,
    on_click_update_a: Callable,
    on_click_update_b: Callable,
) -> rx.Component:
    return rx.card(
        rx.heading(title),
        rx.heading("Alternative view of Data A and B", size="4"),
        rx.grid(
            rx.card("A id:"),
            rx.card(fvars.a_id_copy),
            rx.card("B id:"),
            rx.card(fvars.b_id_copy),
            rx.card("Combined A:"),
            rx.card(fvars.combined_as),
            rx.card("Combined B:"),
            rx.card(fvars.combined_bs),
            flow="row",
            columns="2",
        ),
        rx.grid(
            rx.button("Change A", on_click=on_click_change_a),
            rx.button("Change B", on_click=on_click_change_b),
            rx.button("Update A", on_click=on_click_update_a),
            rx.button("Update B", on_click=on_click_update_b),
            columns="2",
        ),
    )


class ABController(ControllerBase[FrontendVarsA | FrontendVarsB, BackendVars]):
    # Handle processing related to BackedVars (Data A and B)
    # Note: This is a regular class, so no weird inheritance from reflex

    async def change_a(self):
        new_a = DataA(foo=random.randint(0, 100), bar=random.randint(0, 100), baz=random.randint(0, 100))
        bvars = await self.get_bvars()
        await bvars.store(data_a=new_a)
        await self.update_frontend(data_a=new_a, a_id=bvars.a_id)

    async def change_b(self):
        new_b = DataB(fe=str(random.randint(0, 100)), fi=str(random.randint(0, 100)), fo=str(random.randint(0, 100)))
        bvars = await self.get_bvars()
        await bvars.store(data_b=new_b)
        await self.update_frontend(data_b=new_b, b_id=bvars.b_id)


class FullA(rx.ComponentState):
    # This is a ComponentState so that it can define event handlers and use self.state (but doesn't actually store
    # anything in its own state.
    backend_state: ClassVar[type[rx.State]]
    frontend_state: ClassVar[type[rx.State]]

    async def change_a(self):
        return await ABController(self_state=self, backend_state_class=self.backend_state).change_a()

    async def change_b(self):
        return await ABController(self_state=self, backend_state_class=self.backend_state).change_b()

    @classmethod
    def get_component(
        cls,
        frontend_state: FrontendVarsA | type[rx.State],
        backend_state: BackendVars | type[rx.State],
        title: str,
    ) -> rx.Component:
        cls.backend_state = backend_state
        cls.frontend_state = frontend_state
        ABController.register(backend_state=backend_state, frontend_state=frontend_state)
        return display_type_A(fvars=cls.frontend_state, title=title, on_click_a=cls.change_a, on_click_b=cls.change_b)


class FullB(rx.ComponentState):
    backend_state: ClassVar[type[rx.State]]
    frontend_state: ClassVar[type[rx.State]]

    async def change_a(self):
        return await ABController(self_state=self, backend_state_class=self.backend_state).change_a()

    async def change_b(self):
        return await ABController(self_state=self, backend_state_class=self.backend_state).change_b()

    @classmethod
    def get_component(
        cls,
        frontend_state: FrontendVarsB | type[rx.State],
        backend_state: BackendVars | type[rx.State],
        title: str,
    ) -> rx.Component:
        cls.frontend_state = frontend_state
        cls.backend_state = backend_state
        ABController.register(backend_state=backend_state, frontend_state=frontend_state)
        return display_type_B(
            fvars=cls.frontend_state,
            title=title,
            on_click_change_a=cls.change_a,
            on_click_change_b=cls.change_b,
            on_click_update_a=cls.change_a,
            on_click_update_b=cls.change_b,
        )


class BackendVarsState1(BackendVars, rx.State):
    # Could probably use rx.ComponentState and just not render anything with the get_component method, but maybe
    # that's more abstraction than necessary
    """
    Concrete instance of BackendVars 1 -- I.e. multiple things could share this backend state
    """

    pass


class BackendVarsState2(BackendVars, rx.State):
    """
    Concrete instance of BackendVars 2 -- Separate to 1
    """

    pass


class FrontendVarsAState1(FrontendVarsA, rx.State):
    """
    Concrete instance of FrontendVarsA 1 -- matched to backend state 1
    """

    pass


class FrontendVarBState1(FrontendVarsB, rx.State):
    """
    Concrete instance of FrontendVarsB 1 -- matched to backend state 1
    """

    pass


class FrontendVarsAState2(FrontendVarsA, rx.State):
    """
    Concrete instance of FrontendVarsA 2 -- matched to backend state 2
    """

    pass


@template(route="/separation_of_processing_and_display", title="Separation of processing and display")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Separation of processing and display", size="5"),
            rx.markdown(
                dedent("""
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
            """)
            ),
            rx.divider(),
            rx.hstack(
                # rx.card(
                #     rx.heading("DoStuff stuff"),
                #     rx.form(
                #         rx.input(name="input_a", placeholder="Input A"),
                #         rx.input(name="input_b", placeholder="Input B"),
                #         rx.button("Do Stuff"),
                #         on_submit=DoStuffState1.do_stuff,
                #     ),
                #     rx.text(f"State values: {DoStuffState1.bvars.a_id}, {DoStuffState1.bvars.b_id}"),
                # ),
                rx.grid(
                    FullA.create(
                        frontend_state=FrontendVarsAState1,
                        backend_state=BackendVarsState1,
                        title="Display A",
                    ),
                    FullB.create(
                        frontend_state=FrontendVarBState1,
                        backend_state=BackendVarsState1,
                        title="Display B",
                    ),
                    FullA.create(
                        frontend_state=FrontendVarsAState2, backend_state=BackendVarsState2, title="Display C"
                    ),
                    columns="3",
                    width="100%",
                ),
            ),
        ),
        padding="2em",
    )
