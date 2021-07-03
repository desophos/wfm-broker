import asyncio
from quart import Quart, render_template, websocket
from wf_sniper import market

app = Quart(__name__)


@app.route("/")
async def index():
    return await render_template("index.html")


@app.websocket("/ws")
async def ws():
    try:
        async for message in market.subscribe():
            message = message.json()
            if message["type"] == "@WS/SUBSCRIPTIONS/MOST_RECENT/NEW_ORDER":
                order = await market.process_order(message["payload"]["order"])
                if order:
                    await websocket.send_json(order)
    except asyncio.CancelledError:
        await websocket.close(1000)
        raise
