from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

SCRIPT = Path(__file__)
PUBLIC_DIR = (SCRIPT / "../../public").resolve()

app = FastAPI()

app.mount("/static", StaticFiles(directory=PUBLIC_DIR, html=True))


# small little redirect
@app.get("/")
async def index() -> RedirectResponse:
    """Redirect people from the index page to the real (static) index page."""
    return RedirectResponse("/static/")


@app.websocket("/ws")
async def websocket(websocket: WebSocket) -> None:
    """Set up a websocket connection.

    This will be the main websocket connection we will use.
    """
    await websocket.accept()
    await websocket.send_text("Hello, world!")
    await websocket.close()
