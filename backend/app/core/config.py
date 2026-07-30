import os


class Settings:
    # For future use (e.g., model provider, upload dir, etc.)
    upload_dir: str = os.getenv("SYNAPSE_UPLOAD_DIR", "./uploads")


settings = Settings()

