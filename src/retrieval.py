from __future__ import annotations

import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import settings
from src.models import Evidence


class EvidenceIndex:
    def __init__(self, project_id: str) -> None:
        self.project_id = project_id
        self.index_path = settings.vector_dir / f"{project_id}_tfidf.json"
        settings.vector_dir.mkdir(parents=True, exist_ok=True)

    def build(self, evidence_list: list[Evidence]) -> None:
        documents = [self._as_document(item) for item in evidence_list]
        if not documents:
            self.index_path.write_text(
                json.dumps({"documents": [], "documents_text": []}),
                encoding="utf-8",
            )
            return

        payload = {
            "documents": [item.model_dump(mode="json") for item in evidence_list],
            "documents_text": documents,
        }
        self.index_path.write_text(json.dumps(payload), encoding="utf-8")

    def search(self, query: str, limit: int = 5) -> list[tuple[Evidence, float]]:
        if not self.index_path.exists():
            return []

        payload = json.loads(self.index_path.read_text(encoding="utf-8"))
        documents = payload.get("documents", [])
        documents_text = payload.get("documents_text", [])
        if not documents:
            return []

        vectorizer = TfidfVectorizer(stop_words="english")
        doc_matrix = vectorizer.fit_transform(documents_text)
        query_vector = vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, doc_matrix).flatten()
        ranked_indices = similarities.argsort()[::-1][:limit]

        results: list[tuple[Evidence, float]] = []
        for idx in ranked_indices:
            results.append((Evidence.model_validate(documents[idx]), float(similarities[idx])))
        return results

    @staticmethod
    def _as_document(evidence: Evidence) -> str:
        return " ".join(
            [
                evidence.evidence_type,
                evidence.text,
                " ".join(evidence.variables),
                " ".join(evidence.conditions),
            ]
        )
