"""
This is a dummy fastapi application using a database.
"""

import uvicorn

from app.fastapi.routes import routes_and_authentication


app = routes_and_authentication.app


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
