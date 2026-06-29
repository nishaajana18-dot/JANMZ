from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class SimulationResult:
    summary: str
    table: pd.DataFrame


def run_scenario_simulation(
    label: str,
    baseline_mean: float,
    effect_mean: float,
    noise: float,
    trials: int = 250,
) -> SimulationResult:
    rng = np.random.default_rng(42)
    baseline = rng.normal(loc=baseline_mean, scale=max(noise, 0.01), size=trials)
    intervention = rng.normal(
        loc=baseline_mean + effect_mean,
        scale=max(noise, 0.01),
        size=trials,
    )
    lift = intervention - baseline
    success_rate = float((lift > 0).mean())

    table = pd.DataFrame(
        {
            "scenario": ["baseline", label],
            "mean_outcome": [float(baseline.mean()), float(intervention.mean())],
            "std_dev": [float(baseline.std()), float(intervention.std())],
        }
    )
    summary = (
        f"Synthetic simulation only: in {trials} sampled runs, the '{label}' scenario "
        f"beat baseline in about {success_rate:.0%} of runs with an average lift of {float(lift.mean()):.2f}."
    )
    return SimulationResult(summary=summary, table=table)
