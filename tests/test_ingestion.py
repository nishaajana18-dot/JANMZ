from pathlib import Path

from src.ingestion import extract_evidence_fallback, summarize_tabular_file
from src.models import Source


def test_extract_evidence_fallback_labels_limitation() -> None:
    source = Source(
        project_id="p1",
        filename="notes.txt",
        file_type="txt",
        raw_path="notes.txt",
    )
    evidence = extract_evidence_fallback(
        "p1", source, "This study has a limitation because the sample was small."
    )
    assert evidence[0].evidence_type == "limitation"


def test_summarize_tabular_file(tmp_path: Path) -> None:
    csv_path = tmp_path / "demo.csv"
    csv_path.write_text("a,b\n1,2\n3,\n", encoding="utf-8")
    text, metadata = summarize_tabular_file(csv_path)
    assert "Rows: 2" in text
    assert metadata["shape"]["rows"] == 2
    assert "recommended_analyses" in metadata
