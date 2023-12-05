import asyncio
from functools import partial
from operator import eq, gt, not_, truth

from quart import Quart, render_template, websocket
from wfm_broker import market

app = Quart(__name__)


@app.route("/")
async def index():
    return await render_template("index.html")


@app.websocket("/ws")
async def ws():
    await websocket.accept()

    criteria = {
        "order": lambda order: not (
            order["platinum"] == 1 and order["quantity"] != 1
        ),  # user accidentally swapped price and quantity
        "ratio": lambda x: x > 15.0,
        "order_type": partial(eq, "sell"),
        "platform": partial(eq, "pc"),
        "region": partial(eq, "en"),
        "item": lambda item: all(
            test(key in item["tags"])
            for test, key in [(truth, "prime"), (not_, "mod"), (not_, "set")]
        ),
    }

    try:
        async for message in market.subscribe():
            message = message.json()
            if message["type"] == "@WS/SUBSCRIPTIONS/MOST_RECENT/NEW_ORDER":
                order = await market.process_order(
                    message["payload"]["order"], criteria
                )
                if order:
                    app.logger.debug(f"Processed matching order with id {order['id']}")
                    await websocket.send_json(order.data)
                # else:
                #     print(f"Ignored a non-matching order")
    except asyncio.CancelledError:
        await websocket.close(1000)
        raise


def run():
    asyncio.run(app.run_task())
