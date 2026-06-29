from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Type

from pydantic import BaseModel

from src.models import (
    Evidence,
    GapFinding,
    Hypothesis,
    ParsedContent,
    ResearchProject,
    ResearchQuestion,
    Source,
)


MODEL_TABLES: dict[type[BaseModel], str] = {
    ResearchProject: "projects",
    Source: "sources",
    ParsedContent: "parsed_contents",
    Evidence: "evidence",
    GapFinding: "gap_findings",
    ResearchQuestion: "research_questions",
    Hypothesis: "hypotheses",
}


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            for table in MODEL_TABLES.values():
                conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        id TEXT PRIMARY KEY,
                        project_id TEXT,
                        payload TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
            conn.commit()

    @staticmethod
    def _serialize(model: BaseModel) -> str:
        return json.dumps(model.model_dump(mode="json"), ensure_ascii=True)

    @staticmethod
    def _deserialize(model_cls: Type[BaseModel], payload: str) -> BaseModel:
        return model_cls.model_validate_json(payload)

    def upsert(self, model: BaseModel) -> None:
        table = MODEL_TABLES[type(model)]
        project_id = getattr(model, "project_id", getattr(model, "id", None))
        with self._connect() as conn:
            conn.execute(
                f"""
                INSERT INTO {table} (id, project_id, payload, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    project_id=excluded.project_id,
                    payload=excluded.payload,
                    updated_at=excluded.updated_at
                """,
                (
                    model.id,
                    project_id,
                    self._serialize(model),
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()

    def bulk_upsert(self, models: Iterable[BaseModel]) -> None:
        for model in models:
            self.upsert(model)

    def list_all(
        self, model_cls: Type[BaseModel], project_id: str | None = None
    ) -> list[Any]:
        table = MODEL_TABLES[model_cls]
        query = f"SELECT payload FROM {table}"
        params: tuple[Any, ...] = ()
        if project_id:
            query += " WHERE project_id = ?"
            params = (project_id,)
        query += " ORDER BY updated_at DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._deserialize(model_cls, row["payload"]) for row in rows]

    def get(self, model_cls: Type[BaseModel], record_id: str) -> Any | None:
        table = MODEL_TABLES[model_cls]
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT payload FROM {table} WHERE id = ?", (record_id,)
            ).fetchone()
        if not row:
            return None
        return self._deserialize(model_cls, row["payload"])

    def delete_project_data(self, project_id: str) -> None:
        with self._connect() as conn:
            for table in MODEL_TABLES.values():
                conn.execute(f"DELETE FROM {table} WHERE project_id = ?", (project_id,))
            conn.commit()
