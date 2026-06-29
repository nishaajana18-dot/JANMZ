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

BRANCH_QUESTION_OPTIONS: dict[str, list[str]] = {
    "Biomedical and health sciences": [
        "Which biomarker or signal could detect a condition earlier?",
        "Which intervention improves measurable patient or participant outcomes?",
        "What mechanism explains variation in treatment response?",
        "How can a low-cost diagnostic workflow be validated?",
        "Which risk factors predict meaningful clinical change?",
    ],
    "Life and environmental sciences": [
        "Which environmental driver most affects resilience or adaptation?",
        "How does an organism or ecosystem respond under stress?",
        "Which monitoring method detects change most reliably?",
        "What variable explains differences across sites or seasons?",
        "Which intervention improves sustainability or recovery?",
    ],
    "Physical sciences and engineering": [
        "Which material or design parameter improves performance?",
        "What mechanism explains failure, degradation, or inefficiency?",
        "Which operating condition optimizes output under constraints?",
        "How robust is the system across real-world conditions?",
        "Which prototype design is most feasible to test next?",
    ],
    "Data, AI, and computation": [
        "Which model or workflow improves decision quality?",
        "How robust is the method across datasets or user groups?",
        "Which signal or feature improves prediction or explanation?",
        "How can privacy, reliability, or fairness be measured?",
        "What human-AI workflow reduces errors or uncertainty?",
    ],
    "Social and behavioral sciences": [
        "Which factor changes behavior or decision-making?",
        "What intervention improves learning, trust, or adoption?",
        "How does context affect outcomes across groups?",
        "Which policy or program produces measurable impact?",
        "What mechanism links attitudes, incentives, and behavior?",
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


def branch_names() -> list[str]:
    return list(RESEARCH_AREAS.keys())


def topics_for_branch(branch: str) -> list[str]:
    return RESEARCH_AREAS.get(branch, [])


def questions_for_branch(branch: str) -> list[str]:
    return BRANCH_QUESTION_OPTIONS.get(branch, [])
