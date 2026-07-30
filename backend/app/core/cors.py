from fastapi import FastAPI # type: ignore


def add_cors_middleware(app: FastAPI) -> None:
    # In a real deployment, lock this down to your exact frontend origins.
    app.add_middleware(
        "CORSMiddleware",
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

