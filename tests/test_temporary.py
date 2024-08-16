
from typing import Sequence
from unittest import mock
import uuid
import pytest
import reflex as rx
from reflex.state import BaseState

from reflex_test.pages.using_values_in_rx_base import ValsState


def _substate_key(
    token: str,
    state_cls_or_name: BaseState | type[BaseState] | str | Sequence[str],
) -> str:
    """Get the substate key.

    Args:
        token: The token of the state.
        state_cls_or_name: The state class/instance or name or sequence of name parts.

    Returns:
        The substate key.
    """
    if isinstance(state_cls_or_name, BaseState) or (
        isinstance(state_cls_or_name, type) and issubclass(
            state_cls_or_name, BaseState)
    ):
        state_cls_or_name = state_cls_or_name.get_full_name()
    elif isinstance(state_cls_or_name, (list, tuple)):
        state_cls_or_name = ".".join(state_cls_or_name)
    return f"{token}_{state_cls_or_name}"


def app_mockifier(monkeypatch: pytest.MonkeyPatch, app_: rx.App) -> rx.App:
    app_._enable_state()
    app_module = mock.Mock()
    setattr(app_module, rx.constants.CompileVars.APP, app_)

    app_.event_namespace.emit = mock.AsyncMock()  # type: ignore

    def _mock_get_app(*args, **kwargs):
        return app_module

    monkeypatch.setattr(rx.utils.prerequisites, "get_app", _mock_get_app)
    return app_


@pytest.fixture()
def mock_full_app(monkeypatch) -> rx.App:
    from reflex_test.reflex_test import app
    yield app_mockifier(monkeypatch, app)


class TestMockFullApp:
    @pytest.fixture
    def token(self) -> uuid.UUID:
        return uuid.uuid4()

    async def test_a_mock_full_app(self, mock_full_app, token):
        """Picking a simple page from the test app and checking that I can get some values from the state there."""

        app = mock_full_app

        base_state = await app.state_manager.get_state(_substate_key(token, app.state))
        state = await base_state.get_state(ValsState)
        assert state.base.a == 0
        state.base.a = 1
        assert state.base.a == 1

    async def test_b_mock_full_app(self, mock_full_app, token):
        app = mock_full_app

        base_state = await app.state_manager.get_state(_substate_key(token, app.state))
        state = await base_state.get_state(ValsState)
        assert state.base.a == 0, "This will only be true if the tests are independent"
        state.base.a = 3
        assert state.base.a == 3


async def test_ephemeral_app(monkeypatch):
    """Test with a fully self contained app"""
    class SomeState(BaseState):
        a: int = 2

    def page() -> rx.Component:
        return rx.container(rx.text('some state'), rx.text(SomeState.a))

    app = rx.App(state=SomeState)
    app.add_page(page)
    app = app_mockifier(monkeypatch, app)

    token = uuid.uuid4()
    base_state = await app.state_manager.get_state(_substate_key(token, app.state))
    state = await base_state.get_state(SomeState)
    assert state.a == 2
    state.a = 3
    assert state.a == 3
    state.reset()
    assert state.a == 2

    with pytest.raises(RuntimeError):
        # Shouldn't be able to see states outside of this
        state = await base_state.get_state(ValsState)

