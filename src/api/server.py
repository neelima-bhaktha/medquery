import os

import uvicorn


def run_server():
    """
    Launch Uvicorn server for MedQuery FastAPI application.
    """
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    print("\n=======================================================")
    print("       Launching MedQuery FastAPI REST Server          ")
    print(f"       Docs available at: http://localhost:{port}/docs  ")
    print("=======================================================\n")

    uvicorn.run("src.api.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run_server()
