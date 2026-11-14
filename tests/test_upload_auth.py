"""Exercise authorization at the vehicle's HTTP upload boundary."""

from __future__ import annotations

import asyncio
from hashlib import sha256
from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock, PropertyMock, patch

from aiohttp import hdrs
from aiohttp.test_utils import make_mocked_request
import pytest

from custom_components.torque_obd import TorqueView
from custom_components.torque_obd.const import CONF_UPLOAD_TOKEN_HASH, DOMAIN


TOKEN = "example-upload-token"
PAYLOAD = {"k0d": "42", "kff1006": "40.0", "kff1005": "-75.0"}


@pytest.fixture
def upload_view():
    """Provide a vehicle and spies for the upload side effects."""
    options = {CONF_UPLOAD_TOKEN_HASH: sha256(TOKEN.encode()).hexdigest()}
    registry = {"vehicle": SimpleNamespace(options=options)}
    state = {"data": {"k0d": "0"}}
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_get_entry=registry.get),
        data={DOMAIN: {"vehicle": state}},
    )
    view = TorqueView(hass, "vehicle", "/api/torque-vehicle")
    with (
        patch.object(view, "_create_sensors_for_new_data", new_callable=AsyncMock) as discover,
        patch("custom_components.torque_obd.async_dispatcher_send") as dispatch,
    ):
        yield view, options, state, discover, dispatch


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize(
    "authorization",
    [
        [],
        ["Bearer wrong-token"],
        [f"Basic {TOKEN}"],
        ["Bearer"],
        ["Bearer café"],
        [f"Bearer {TOKEN}", "Bearer wrong-token"],
    ],
)
def test_rejected_upload_bypasses_telemetry_parsing(upload_view, method, authorization):
    """A token in the URL cannot substitute for a valid authorization header."""
    view, _, state, discover, dispatch = upload_view
    request = make_mocked_request(
        method,
        f"{view.url}?upload_token={TOKEN}&k0d=42",
        headers=[(hdrs.AUTHORIZATION, value) for value in authorization],
    )
    request.post = AsyncMock(side_effect=AssertionError("POST body was parsed"))
    with patch.object(type(request), "query", new_callable=PropertyMock) as query:
        response = asyncio.run(getattr(view, method.lower())(request))

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert response.headers[hdrs.WWW_AUTHENTICATE] == "Bearer"
    request.post.assert_not_awaited()
    query.assert_not_called()
    assert state["data"] == {"k0d": "0"}
    discover.assert_not_awaited()
    dispatch.assert_not_called()


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("protected", [False, True])
def test_accepted_upload_dispatches_vehicle_data(upload_view, method, protected):
    """Legacy and token-protected vehicles ingest readings through the same path."""
    view, options, state, discover, dispatch = upload_view
    headers = {hdrs.AUTHORIZATION: f"bearer {TOKEN}"} if protected else {}
    if not protected:
        options.clear()
    request = make_mocked_request(method, f"{view.url}?k0d=42", headers=headers)
    request.post = AsyncMock(return_value=PAYLOAD)
    response = asyncio.run(getattr(view, method.lower())(request))

    assert response.status == HTTPStatus.OK
    assert response.text == "OK!"
    expected = PAYLOAD if method == "POST" else {"k0d": "42"}
    assert state["data"] == expected
    discover.assert_awaited_once_with(expected)
    dispatch.assert_called_once_with(view.hass, f"{DOMAIN}_vehicle_update", expected)


def test_rotation_during_post_rejects_old_token(upload_view):
    """An upload authorized before rotation cannot write after body parsing."""
    view, options, state, discover, dispatch = upload_view

    async def rotate_token():
        options[CONF_UPLOAD_TOKEN_HASH] = sha256(b"replacement-token").hexdigest()
        return PAYLOAD

    request = make_mocked_request(
        "POST", view.url, headers={hdrs.AUTHORIZATION: f"Bearer {TOKEN}"}
    )
    request.post = AsyncMock(side_effect=rotate_token)
    response = asyncio.run(view.post(request))

    assert response.status == HTTPStatus.UNAUTHORIZED
    assert state["data"] == {"k0d": "0"}
    discover.assert_not_awaited()
    dispatch.assert_not_called()


def test_vehicle_routes_can_share_a_token(upload_view):
    """The token authorizes uploads and the URL still selects the vehicle."""
    first_view, options, first_state, _, dispatch = upload_view
    second_view = TorqueView(first_view.hass, "second", "/api/torque-second")
    second_state = {"data": {}}
    first_view.hass.data[DOMAIN]["second"] = second_state
    entries = {
        "vehicle": SimpleNamespace(options=options),
        "second": SimpleNamespace(options=dict(options)),
    }
    first_view.hass.config_entries.async_get_entry = entries.get
    headers = {hdrs.AUTHORIZATION: f"Bearer {TOKEN}"}

    with patch.object(second_view, "_create_sensors_for_new_data", new_callable=AsyncMock):
        first_response = asyncio.run(first_view.get(
            make_mocked_request("GET", f"{first_view.url}?k0d=42", headers=headers)
        ))
        second_response = asyncio.run(second_view.get(
            make_mocked_request("GET", f"{second_view.url}?k0d=75", headers=headers)
        ))

    assert first_response.status == second_response.status == HTTPStatus.OK
    assert first_state["data"] == {"k0d": "42"}
    assert second_state["data"] == {"k0d": "75"}
    assert [call.args[1] for call in dispatch.call_args_list] == [
        f"{DOMAIN}_vehicle_update",
        f"{DOMAIN}_second_update",
    ]
