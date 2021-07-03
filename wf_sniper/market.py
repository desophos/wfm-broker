import json
from quart import g
import aiohttp


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


async def process_order(order, criteria={}):
    if (
        order["order_type"] == "sell"
        and order["platform"] == "pc"
        and order["region"] == "en"
        and "prime" in order["item"]["tags"]
        and "mod" not in order["item"]["tags"]
        and "set" not in order["item"]["tags"]
    ):
        try:
            item_ducats = (await ducats())[order["item"]["id"]]
            order_ratio = item_ducats / order["platinum"]

            if order_ratio < 8.0 or (  # TODO: TEMPORARY MAGIC NUMBER
                order["platinum"] == 1 and order["quantity"] != 1
            ):
                # ratio isn't good enough for us or
                # user accidentally swapped price and quantity
                return None
            else:
                order["ratio"] = order_ratio
                order["item"]["ducats"] = item_ducats
                return order

        except KeyError:
            with open("error.log", "a") as f:
                json.dump(order, f)
                return None


async def ducats():
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
