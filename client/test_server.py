"""This is a basic echo server, it's only meant to test the client."""

import asyncio

import websockets


async def echo(websocket):
    async for message in websocket:
        print(message)
        await websocket.send(message)


async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
