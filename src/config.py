from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_root: Path = Path(__file__).resolve().parent.parent
    db_path: Path = Path(os.getenv("APP_DB_PATH", "data/app.db"))
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
    processed_dir: Path = Path(os.getenv("PROCESSED_DIR", "data/processed"))
    vector_dir: Path = Path(os.getenv("VECTOR_DIR", "data/vector_store"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_embedding_model: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )

    def ensure_directories(self) -> None:
        for path in (
            self.db_path.parent,
            self.upload_dir,
            self.processed_dir,
            self.vector_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
