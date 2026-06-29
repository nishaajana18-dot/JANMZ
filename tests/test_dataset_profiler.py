import pandas as pd

from src.dataset_profiler import profile_dataframe


def test_profile_dataframe_is_domain_agnostic() -> None:
    df = pd.DataFrame(
        {
            "temperature": [20.0, 21.5, 23.1],
            "efficiency": [0.7, 0.72, 0.78],
            "material": ["a", "b", "a"],
        }
    )
    profile = profile_dataframe(df)
    assert profile["shape"]["rows"] == 3
    assert "temperature" in profile["numeric_columns"]
    assert "efficiency" in profile["candidate_target_columns"]
    assert "correlation analysis" in profile["recommended_analyses"]
