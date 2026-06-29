from __future__ import annotations


RESEARCH_AREAS: dict[str, list[str]] = {
    "Biomedical and health sciences": [
        "Diagnostics and biomarkers",
        "Drug delivery",
        "Public health interventions",
        "Neuroscience",
        "Wearables and remote monitoring",
    ],
    "Life and environmental sciences": [
        "Climate adaptation",
        "Plant resilience",
        "Microbiome dynamics",
        "Biodiversity monitoring",
        "Water systems",
    ],
    "Physical sciences and engineering": [
        "Battery materials",
        "Photonics",
        "Robotics",
        "Advanced manufacturing",
        "Renewable energy systems",
    ],
    "Data, AI, and computation": [
        "Human-AI collaboration",
        "Model robustness",
        "Scientific machine learning",
        "Privacy-preserving analytics",
        "Decision support systems",
    ],
    "Social and behavioral sciences": [
        "Learning outcomes",
        "Behavior change",
        "Trust and risk perception",
        "Workplace productivity",
        "Policy evaluation",
    ],
}

QUESTION_LENSES: dict[str, str] = {
    "Mechanism": "What underlying mechanism could explain the observed pattern?",
    "Comparison": "Which intervention, material, or strategy performs better under matched conditions?",
    "Optimization": "What parameter range is most likely to improve the target outcome?",
    "Robustness": "Does the effect still hold across constraints, subgroups, or settings?",
    "Translation": "What is the smallest practical experiment that could move this toward real-world use?",
}

HYPOTHESIS_LENSES: list[dict[str, str]] = [
    {
        "type": "mechanistic",
        "label": "Mechanistic",
        "description": "Explains why a pattern may happen.",
    },
    {
        "type": "comparative",
        "label": "Comparative",
        "description": "Compares two strategies or conditions.",
    },
    {
        "type": "optimization",
        "label": "Optimization",
        "description": "Looks for a better setting or operating range.",
    },
    {
        "type": "robustness",
        "label": "Robustness",
        "description": "Tests whether an effect survives under constraints.",
    },
    {
        "type": "translational",
        "label": "Translational",
        "description": "Moves an idea toward a deployable experiment.",
    },
]
