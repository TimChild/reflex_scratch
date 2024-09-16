from __future__ import annotations
import os
from typing import TYPE_CHECKING
from unittest import mock
import uuid
import pytest
import reflex as rx
from reflex.state import StateManagerRedis, _substate_key, BaseState
from selenium.webdriver.remote.webdriver import (
    WebDriver,
)
from selenium.webdriver.common.by import By

if TYPE_CHECKING:
    from reflex.testing import AppHarness


def app_fn() -> None:
    import reflex as rx

    class SomeState(rx.State):
        var_a: int = 1

        def increment_var_a(self) -> None:
            self.var_a += 1

    @rx.page()
    def index() -> rx.Component:
        return rx.container(
            rx.heading("Hello World"),
            rx.text("SomeState.var_a: "),
            rx.text(SomeState.var_a, id="text-output"),
            rx.button("Increment", id="button-increment", on_click=SomeState.increment_var_a),
        )

    app = rx.App()


@pytest.fixture(scope="module")
def app_harness(tmp_path_factory):
    from reflex.testing import AppHarness

    with AppHarness.create(
        root=tmp_path_factory.mktemp("app_harness_root"),
        app_source=app_fn,
    ) as harness:
        assert harness.app_instance is not None, "app not running"
        yield harness


TIMEOUT = 5


@pytest.fixture(scope="module")
def driver(app_harness):
    driver = app_harness.frontend()
    try:
        yield driver
    finally:
        driver.quit()


def test_harness(app_harness: AppHarness, driver: WebDriver):
    """Tests by building the app and hosting locally -- slow but good for full integration"""
    button = driver.find_element(By.ID, "button-increment")
    value_text = driver.find_element(By.ID, "text-output")
    assert value_text.text == "1"
    button.click()
    assert app_harness.poll_for_content(value_text, timeout=TIMEOUT, exp_not_equal="1") == "2"


class SomeState(rx.State):
    var_a: int = 1


def create_token(state: type[rx.State]) -> str:
    return _substate_key(str(uuid.uuid4()), state)
    # return str(uuid.uuid4()) + f"_{state.get_full_name()}"


async def test_get_set_state_attr(mock_app):
    """Test more directly altering states"""
    state_class = SomeState
    app = rx.App(state=state_class)

    token1 = create_token(state_class)
    token2 = create_token(state_class)

    state1 = await app.state_manager.get_state(token1)
    state2 = await app.state_manager.get_state(token2)
    assert state1.var_a == 1
    assert state2.var_a == 1

    state1.var_a = 5
    state2.var_a += 1

    await app.state_manager.set_state(token1, state1)
    await app.state_manager.set_state(token2, state2)

    state1 = await app.state_manager.get_state(token1)
    state2 = await app.state_manager.get_state(token2)
    assert state1.var_a == 5
    assert state2.var_a == 2

    if isinstance(app.state_manager, StateManagerRedis):
        await app.state_manager.close()


@pytest.fixture
def token() -> str:
    return str(uuid.uuid4())


@pytest.fixture(scope="function")
def mock_app(monkeypatch) -> rx.App:
    """Mock app fixture.

    Args:
        monkeypatch: Pytest monkeypatch object.
        state_manager: A state manager.

    Returns:
        The app, after mocking out prerequisites.get_app()
    """
    app = rx.App(state=rx.State)

    app_module = mock.Mock()

    setattr(app_module, rx.constants.CompileVars.APP, app)
    app.event_namespace.emit = mock.AsyncMock()  # type: ignore

    def _mock_get_app(*args, **kwargs):
        return app_module

    monkeypatch.setattr(rx.utils.prerequisites, "get_app", _mock_get_app)
    return app


async def test_get_another_state_from_regular_callback(mock_app, token):
    class MyBaseState(BaseState):
        pass

    class StateA(MyBaseState):
        var_a: int = 1

        async def handler_that_gets_other_state(self):
            other_state = await self.get_state(StateB)
            self.var_a = other_state.var_b

    class ChildStateA(StateA):
        child_a: int = 3

    class StateB(MyBaseState):
        var_b: int = 2

        @rx.background
        async def get_child_a_value_background(self):
            async with self:
                child_a = await self.get_state(ChildStateA)
            self.var_b = child_a.child_a

    app = mock_app
    app.state = MyBaseState
    app.state_manager.state = MyBaseState

    # First try getting state from state_manager directly
    base_state = await app.state_manager.get_state(_substate_key(token, MyBaseState))
    # Note: Trying to get anything but the root state from state_manager does not seem to work...
    state_a = await app.state_manager.get_state(_substate_key(token, StateA))
    # <<< Note: instance of the BaseState NOT StateA!
    assert isinstance(state_a, MyBaseState)
    assert state_a is base_state

    # But using the .get_state method on the state instance works
    state_a = await base_state.get_state(StateA)
    assert isinstance(state_a, StateA)

    # Then use state to get other state
    state_b = await state_a.get_state(StateB)
    assert isinstance(state_b, StateB)

    # Check values before calling handler method
    assert state_a.var_a == 1
    assert state_b.var_b == 2

    # Call handler method
    await state_a.handler_that_gets_other_state()
    assert state_a.var_a == 2

    # But trying to call a method that is a background task does not work...
    with pytest.raises(RuntimeError):
        await state_b.get_child_a_value_background()
