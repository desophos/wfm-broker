import json
from logging import getLogger
from typing import Any, Callable, Mapping

import aiohttp
from quart import g

logger = getLogger(__name__)

class Order:
    FIELDS = [
        "id",
        "platinum",
        "quantity",
        "order_type",
        "platform",
        "region",
        "creation_date",
        "last_update",
        "user",
        "item",
    ]

    def __init__(self, data: Mapping[str, Any]):
        self.data = {}
        for key in self.FIELDS:
            if key in data:
                self.data[key] = data[key]
            else:
                raise InvalidOrderError(self, f"key '{key}' not found in order data")

        if self["platinum"] < 1:
            raise InvalidOrderError(
                self, f"platinum must be >= 1, not {self['platinum']}"
            )

    def __getitem__(self, key: str):
        return self.data[key]

    def __setitem__(self, key: str, val):
        self.data[key] = val

    def __str__(self) -> str:
        return self.id


class InvalidOrderError(Exception):
    def __init__(self, order, msg):
        self.order = order
        self.message = f"Invalid order with ID {order.id}: {msg}"


class InvalidCriteriaError(Exception):
    def __init__(self, criteria, msg):
        self.criteria = criteria
        self.message = f"Invalid criteria: {msg}"


async def get_ducats():
    if not hasattr(g, "ducats"):
        async with aiohttp.ClientSession(
            headers={"platform": "pc", "language": "en"}
        ) as session:

            async with session.get(
                "https://api.warframe.market/v1/tools/ducats"
            ) as response:

                response = await response.json()

                g.ducats = {
                    entry["item"]: entry["ducats"]
                    for entry in response["payload"]["previous_day"]
                }
    return g.ducats


async def subscribe():
    async with aiohttp.ClientSession(
        headers={"platform": "pc", "language": "en"}
    ) as session:
        async with session.ws_connect(
            "wss://warframe.market/socket",
            headers={
                "Authorization": "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzaWQiOiJLYlFhRkw5ZjVubkFzekk3djlsSWpzbFBJZGZKalZLUCIsImNzcmZfdG9rZW4iOiJiMWYwNjg3MDc1YTExZWZjYzczZjg0OGQ5NzI2MDNiZDllZWQ5YjJkIiwiZXhwIjoxNTYwNTg0MTA3LCJpYXQiOjE1NTU0MDAxMDcsImlzcyI6Imp3dCIsImF1ZCI6Imp3dCIsImF1dGhfdHlwZSI6ImNvb2tpZSIsInNlY3VyZSI6ZmFsc2UsImp3dF9pZGVudGl0eSI6IkpnM3c4Z2VpTFJWQjU0eE5NYUhHMnc5emZHYzdRaDZBIiwibG9naW5fdWEiOiJiJ01vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjY0LjApIEdlY2tvLzIwMTAwMTAxIEZpcmVmb3gvNjQuMCciLCJsb2dpbl9pcCI6ImInMjA3LjE4MS4yMTAuOTYnIn0.gA6PlbOYRWc0eJOHtmwlWEm9MhRiVubIVMGSNAb6VAI"
            },
        ) as websocket:
            await websocket.send_json({"type": "@WS/SUBSCRIBE/MOST_RECENT"})
            async for message in websocket:
                yield message


async def process_order(order_data, criteria: Mapping[str, Callable[[Any], Any]] = {}):
    order = Order(order_data)

    try:
        ducats = (await get_ducats()).get(order["item"]["id"], 0)
        order["item"]["ducats"] = ducats

        ratio = ducats / order["platinum"]
        order["ratio"] = ratio

        valid = True
        for key, fn in criteria.items():
            if key == "order":
                valid = valid and fn(order)
            else:
                try:
                    valid = valid and fn(order[key])
                except KeyError as e:
                    raise InvalidCriteriaError(
                        criteria, f"'{key}' is not a valid order field"
                    ) from e

        return order if valid else None

    except KeyError as e:
        with open("error.log", "a") as f:
            msg = f"KeyError({str(e)}): {json.dumps(order.data, f)}"
            logger.error(msg)
            f.write(msg + "\n")
            return None
