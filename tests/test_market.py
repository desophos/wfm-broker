from operator import truth

import pytest
from quart import g
from wfm_broker.market import get_ducats, process_order, subscribe

from tests.conftest import dummy_order


@pytest.mark.asyncio
async def test_get_ducats(app):
    async with app.app_context():
        assert await get_ducats()
        assert hasattr(g, "ducats")


@pytest.mark.asyncio
async def test_subscribe():
    # async with client.websocket('/ws') as ws:
    async for message in subscribe():
        if message["type"] == "@WS/SUBSCRIPTIONS/MOST_RECENT/NEW_ORDER":
            assert message["payload"]["order"]
            return True  # just check for first message


@pytest.mark.parametrize(
    "expected,data,criteria",
    [
        (truth, {}, {}),
    ],
)  # TODO: more test cases
@pytest.mark.asyncio
async def test_process_order(app, dummy_order, expected, data, criteria):
    async with app.app_context():
        g.ducats = {"test": 100}
        assert expected(await process_order(dummy_order(data), criteria))
