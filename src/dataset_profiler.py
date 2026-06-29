from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError(f"Unsupported dataset file type: {path.suffix}")


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    numeric_columns = df.select_dtypes(include="number").columns.astype(str).tolist()
    categorical_columns = df.select_dtypes(exclude="number").columns.astype(str).tolist()
    missingness = {
        str(column): int(count) for column, count in df.isna().sum().to_dict().items()
    }
    profile = {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": df.columns.astype(str).tolist(),
        "dtypes": {str(key): str(value) for key, value in df.dtypes.to_dict().items()},
        "missing_values": missingness,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "candidate_target_columns": candidate_target_columns(df),
        "candidate_predictor_columns": candidate_predictor_columns(df),
        "simple_relationships": simple_relationships(df),
        "recommended_analyses": recommend_analyses(df),
        "inferred_dataset_type": infer_dataset_type(df),
    }
    return profile


def profile_table(path: Path) -> dict[str, Any]:
    return profile_dataframe(load_table(path))


def candidate_target_columns(df: pd.DataFrame) -> list[str]:
    names = df.columns.astype(str).tolist()
    target_keywords = [
        "target",
        "outcome",
        "response",
        "label",
        "class",
        "yield",
        "score",
        "rate",
        "survival",
        "time",
        "temperature",
        "efficiency",
    ]
    matches = [
        name for name in names if any(keyword in name.lower() for keyword in target_keywords)
    ]
    if matches:
        return matches[:5]
    numeric = df.select_dtypes(include="number").columns.astype(str).tolist()
    return numeric[-3:] if numeric else names[-3:]


def candidate_predictor_columns(df: pd.DataFrame) -> list[str]:
    targets = set(candidate_target_columns(df))
    return [name for name in df.columns.astype(str).tolist() if name not in targets][:12]


def simple_relationships(df: pd.DataFrame) -> list[dict[str, Any]]:
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        return []
    correlations = numeric_df.corr(numeric_only=True).abs()
    relationships: list[dict[str, Any]] = []
    for left in correlations.columns:
        for right in correlations.columns:
            if left >= right:
                continue
            value = correlations.loc[left, right]
            if pd.notna(value):
                relationships.append(
                    {
                        "variables": [str(left), str(right)],
                        "relationship": "absolute correlation",
                        "strength": round(float(value), 3),
                    }
                )
    return sorted(relationships, key=lambda item: item["strength"], reverse=True)[:8]


def recommend_analyses(df: pd.DataFrame) -> list[str]:
    numeric_count = len(df.select_dtypes(include="number").columns)
    categorical_count = len(df.select_dtypes(exclude="number").columns)
    columns = [column.lower() for column in df.columns.astype(str)]
    recommendations = ["dataset quality check", "missingness analysis"]

    if numeric_count >= 2:
        recommendations.extend(["correlation analysis", "linear regression"])
    if categorical_count >= 1 and numeric_count >= 1:
        recommendations.extend(["group comparison", "classification"])
    if numeric_count >= 4:
        recommendations.extend(["clustering", "dimensionality reduction"])
    if any("time" in column or "date" in column for column in columns):
        recommendations.append("time-series analysis")
    if any("survival" in column or "duration" in column for column in columns):
        recommendations.append("survival analysis")
    if numeric_count >= 1:
        recommendations.extend(["simulation comparison", "ablation studies"])

    return list(dict.fromkeys(recommendations))


def infer_dataset_type(df: pd.DataFrame) -> str:
    columns = " ".join(df.columns.astype(str)).lower()
    if "time" in columns or "date" in columns:
        return "time-indexed or longitudinal"
    if "lat" in columns or "lon" in columns or "location" in columns:
        return "spatial or environmental"
    if "label" in columns or "class" in columns or "target" in columns:
        return "supervised learning or classification"
    if len(df.select_dtypes(include="number").columns) >= 4:
        return "multivariate numeric"
    return "general tabular"


def profile_to_markdown(profile: dict[str, Any], title: str = "Dataset") -> str:
    lines = [
        f"### {title}",
        f"- Shape: {profile['shape']['rows']} rows x {profile['shape']['columns']} columns",
        f"- Inferred type: {profile['inferred_dataset_type']}",
        f"- Numeric columns: {', '.join(profile['numeric_columns']) or 'None'}",
        f"- Categorical columns: {', '.join(profile['categorical_columns']) or 'None'}",
        f"- Candidate targets: {', '.join(profile['candidate_target_columns']) or 'None'}",
        f"- Candidate predictors: {', '.join(profile['candidate_predictor_columns']) or 'None'}",
        f"- Recommended analyses: {', '.join(profile['recommended_analyses'])}",
    ]
    if profile["simple_relationships"]:
        lines.append("- Strongest simple relationships:")
        for item in profile["simple_relationships"][:5]:
            variables = " / ".join(item["variables"])
            lines.append(f"  - {variables}: {item['strength']}")
    return "\n".join(lines)
