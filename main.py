# simply re-export the app to make commands simpler
from server.main import app

__all__ = ("app",)
