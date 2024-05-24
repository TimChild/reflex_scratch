import asyncio
import datetime
import uuid
from typing import Generator
from unittest.mock import Mock, AsyncMock
import reflex as rx
import plotly.graph_objects as go

import pytest
from reflex import App
from reflex.constants import CompileVars
from reflex.state import StateManager, StateManagerRedis, StateManagerMemory, _substate_key, BaseState
from reflex.utils import prerequisites
from reflex.vars import ComputedVar


class Object(rx.Base):
    """A test object fixture."""

    prop1: int = 42
    prop2: str = "hello"


class TestState(BaseState):
    """A test state."""

    # Set this class as not test one
    __test__ = False

    num1: int
    num2: float = 3.14
    key: str
    map_key: str = "a"
    array: list[float] = [1, 2, 3.14]
    mapping: dict[str, list[int]] = {"a": [1, 2, 3], "b": [4, 5, 6]}
    obj: Object = Object()
    complex: dict[int, Object] = {1: Object(), 2: Object()}
    fig: go.Figure = go.Figure()
    dt: datetime.datetime = datetime.datetime.fromisoformat("1989-11-09T18:53:00+01:00")

    @ComputedVar
    def sum(self) -> float:
        """Dynamically sum the numbers.

        Returns:
            The sum of the numbers.
        """
        return self.num1 + self.num2

    @ComputedVar
    def upper(self) -> str:
        """Uppercase the key.

        Returns:
            The uppercased key.
        """
        return self.key.upper()

    def do_something(self):
        """Do something."""
        pass


class MyState(TestState):
    something: str = "something"


class ChildState(TestState):
    """A child state fixture."""

    value: str
    count: int = 23

    def change_both(self, value: str, count: int):
        """Change both the value and count.

        Args:
            value: The new value.
            count: The new count.
        """
        self.value = value.upper()
        self.count = count * 2


class ChildState2(TestState):
    """A child state fixture."""

    value: str


class ChildState3(TestState):
    """A child state fixture."""

    value: str


class GrandchildState(ChildState):
    """A grandchild state fixture."""

    value2: str

    def do_nothing(self):
        """Do something."""
        pass


class GrandchildState2(ChildState2):
    """A grandchild state fixture."""

    @rx.cached_var
    def cached(self) -> str:
        """A cached var.

        Returns:
            The value.
        """
        return self.value


class GrandchildState3(ChildState3):
    """A great grandchild state fixture."""

    @rx.var
    def computed(self) -> str:
        """A computed var.

        Returns:
            The value.
        """
        return self.value


class DateTimeState(BaseState):
    """A State with some datetime fields."""

    d: datetime.date = datetime.date.fromisoformat("1989-11-09")
    dt: datetime.datetime = datetime.datetime.fromisoformat("1989-11-09T18:53:00+01:00")
    t: datetime.time = datetime.time.fromisoformat("18:53:00+01:00")
    td: datetime.timedelta = datetime.timedelta(days=11, minutes=11)


@pytest.fixture
def token() -> str:
    return str(uuid.uuid4())


@pytest.fixture(scope="function", params=["in_process", "redis"])
def state_manager(request) -> Generator[StateManager, None, None]:
    """Instance of state manager parametrized for redis and in-process.

    Args:
        request: pytest request object.

    Yields:
        A state manager instance
    """
    state_manager = StateManager.create(state=TestState)
    if request.param == "redis":
        if not isinstance(state_manager, StateManagerRedis):
            pytest.skip("Test requires redis")
    else:
        # explicitly NOT using redis
        state_manager = StateManagerMemory(state=TestState)
        assert not state_manager._states_locks

    yield state_manager

    if isinstance(state_manager, StateManagerRedis):
        asyncio.get_event_loop().run_until_complete(state_manager.close())


@pytest.fixture(scope="function")
def mock_app(monkeypatch, state_manager: StateManager) -> rx.App:
    """Mock app fixture.

    Args:
        monkeypatch: Pytest monkeypatch object.
        state_manager: A state manager.

    Returns:
        The app, after mocking out prerequisites.get_app()
    """
    app = App(state=TestState)

    app_module = Mock()

    setattr(app_module, CompileVars.APP, app)
    app.state = TestState
    app._state_manager = state_manager
    app.event_namespace.emit = AsyncMock()  # type: ignore

    def _mock_get_app(*args, **kwargs):
        return app_module

    monkeypatch.setattr(prerequisites, "get_app", _mock_get_app)
    return app


@pytest.mark.asyncio
async def test_get_state(mock_app: rx.App, token: str):
    """Test that a get_state populates the top level state and delta calculation is correct.

    Args:
        mock_app: An app that will be returned by `get_app()`
        token: A token.
    """
    mock_app.state_manager.state = mock_app.state = TestState

    # Get instance of ChildState2.
    test_state = await mock_app.state_manager.get_state(_substate_key(token, ChildState2))
    assert isinstance(test_state, TestState)
    if isinstance(mock_app.state_manager, StateManagerMemory):
        # All substates are available
        assert tuple(sorted(test_state.substates)) == ("child_state", "child_state2", "child_state3", "my_state")
    else:
        # Sibling states are only populated if they have computed vars
        assert tuple(sorted(test_state.substates)) == ("child_state2", "child_state3")

    # Because ChildState3 has a computed var, it is always dirty, and always populated.
    assert test_state.substates["child_state3"].substates["grandchild_state3"].computed == ""

    # Get the child_state2 directly.
    child_state2_direct = test_state.get_substate(["child_state2"])
    child_state2_get_state = await test_state.get_state(ChildState2)
    # These should be the same object.
    assert child_state2_direct is child_state2_get_state

    my_state = await test_state.get_state(MyState)
    assert isinstance(my_state, MyState)
    assert my_state.something == "something"

    # Get arbitrary GrandchildState.
    grandchild_state = await child_state2_get_state.get_state(GrandchildState)
    assert isinstance(grandchild_state, GrandchildState)

    # Now the original root should have all substates populated.
    assert tuple(sorted(test_state.substates)) == (
        "child_state",
        "child_state2",
        "child_state3",
        "my_state",
    )

    # ChildState should be retrievable
    child_state_direct = test_state.get_substate(["child_state"])
    child_state_get_state = await test_state.get_state(ChildState)
    # These should be the same object.
    assert child_state_direct is child_state_get_state

    # GrandchildState instance should be the same as the one retrieved from the child_state2.
    assert grandchild_state is child_state_direct.get_substate(["grandchild_state"])
    grandchild_state.value2 = "set_value"

    assert test_state.get_delta() == {
        TestState.get_full_name(): {
            "sum": 3.14,
            "upper": "",
        },
        GrandchildState.get_full_name(): {
            "value2": "set_value",
        },
        GrandchildState3.get_full_name(): {
            "computed": "",
        },
    }

    # Get a fresh instance
    new_test_state = await mock_app.state_manager.get_state(_substate_key(token, ChildState2))
    assert isinstance(new_test_state, TestState)
    if isinstance(mock_app.state_manager, StateManagerMemory):
        # In memory, it's the same instance
        assert new_test_state is test_state
        test_state._clean()
        # All substates are available
        assert tuple(sorted(new_test_state.substates)) == (
            "child_state",
            "child_state2",
            "child_state3",
            "my_state",
        )
    else:
        # With redis, we get a whole new instance
        assert new_test_state is not test_state
        # Sibling states are only populated if they have computed vars
        assert tuple(sorted(new_test_state.substates)) == (
            "child_state2",
            "child_state3",
        )

    # Set a value on child_state2, should update cached var in grandchild_state2
    child_state2 = new_test_state.get_substate(("child_state2",))
    child_state2.value = "set_c2_value"

    assert new_test_state.get_delta() == {
        TestState.get_full_name(): {
            "sum": 3.14,
            "upper": "",
        },
        ChildState2.get_full_name(): {
            "value": "set_c2_value",
        },
        GrandchildState2.get_full_name(): {
            "cached": "set_c2_value",
        },
        GrandchildState3.get_full_name(): {
            "computed": "",
        },
    }
