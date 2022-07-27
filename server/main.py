import asyncio
import json

import websockets

connections = set()


async def register(websocket):
    """Adds a player's connections to connections and removes them when they disconnect."""
    connections.add(websocket)
    try:
        await handler(websocket)
    finally:
        connections.remove(websocket)


async def handler(websocket):
    async for message in websocket:
        event = json.loads(message)
        print(event)  # TODO: remove this later.
        match event["type"]:
            case "chat":
                response = json.dumps(
                    {"type": "chat", "chat_message": event["chat_message"]}
                )
                websockets.broadcast(connections, response)


async def main():
    async with websockets.serve(register, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
