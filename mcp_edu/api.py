from fastapi import FastAPI

def create_app():
    app = FastAPI(title="MCP Schools – MVP")
    @app.get("/ping")
    async def ping():
        return {"pong": True}
    return app
