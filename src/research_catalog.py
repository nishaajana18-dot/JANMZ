from __future__ import annotations

from typing import Any


SCIENCE_TREE: dict[str, dict[str, dict[str, dict[str, list[str]]]]] = {
    "Physics": {
        "Biophysics": {
            "Molecular biophysics": {
                "topics": [
                    "Protein folding dynamics",
                    "Membrane transport",
                    "Single-molecule force spectroscopy",
                ],
                "questions": [
                    "Which molecular interaction most changes stability or function?",
                    "How does the physical environment alter biological transport?",
                    "What measurable signal best captures conformational change?",
                ],
            },
            "Medical physics": {
                "topics": [
                    "Radiation dose optimization",
                    "Imaging contrast",
                    "Therapy planning",
                ],
                "questions": [
                    "Which imaging parameter improves signal while limiting dose?",
                    "How can a treatment plan be made more robust to uncertainty?",
                    "What physical metric predicts therapeutic response?",
                ],
            },
        },
        "Mechanics": {
            "Fluid mechanics": {
                "topics": [
                    "Turbulence control",
                    "Microfluidics",
                    "Boundary-layer flow",
                ],
                "questions": [
                    "Which flow condition changes drag, mixing, or transport most?",
                    "How does geometry alter stability or throughput?",
                    "What control strategy reduces unwanted turbulence?",
                ],
            },
            "Solid mechanics": {
                "topics": [
                    "Fracture mechanics",
                    "Soft materials",
                    "Fatigue testing",
                ],
                "questions": [
                    "Which material property best predicts failure?",
                    "How do repeated loads change stiffness or fracture risk?",
                    "What design change improves mechanical resilience?",
                ],
            },
        },
        "Quantum physics": {
            "Quantum information": {
                "topics": [
                    "Qubit error mitigation",
                    "Quantum sensing",
                    "Entanglement verification",
                ],
                "questions": [
                    "Which noise source most limits quantum performance?",
                    "How can error mitigation improve usable signal?",
                    "What measurement verifies entanglement most reliably?",
                ],
            },
            "Condensed matter": {
                "topics": [
                    "Topological materials",
                    "Superconductivity",
                    "Spin transport",
                ],
                "questions": [
                    "Which material condition produces the target electronic state?",
                    "How does temperature or disorder change transport?",
                    "What signature distinguishes competing physical mechanisms?",
                ],
            },
        },
    },
    "Biology": {
        "Molecular biology": {
            "Gene regulation": {
                "topics": [
                    "Transcription factor binding",
                    "Epigenetic regulation",
                    "RNA stability",
                ],
                "questions": [
                    "Which regulatory element changes gene expression most?",
                    "How does perturbation alter downstream pathway activity?",
                    "What mechanism explains differences across cell states?",
                ],
            },
            "Cell signaling": {
                "topics": [
                    "Signal transduction",
                    "Receptor dynamics",
                    "Stress response pathways",
                ],
                "questions": [
                    "Which signaling node controls the observed response?",
                    "How does timing affect pathway activation?",
                    "What feedback loop stabilizes or amplifies the signal?",
                ],
            },
        },
        "Ecology": {
            "Population ecology": {
                "topics": [
                    "Species interactions",
                    "Habitat fragmentation",
                    "Population resilience",
                ],
                "questions": [
                    "Which environmental driver most changes population growth?",
                    "How does fragmentation alter movement or survival?",
                    "What intervention improves ecosystem resilience?",
                ],
            },
            "Microbiome ecology": {
                "topics": [
                    "Community assembly",
                    "Host-microbe interactions",
                    "Antibiotic perturbation",
                ],
                "questions": [
                    "Which taxa or function predicts community stability?",
                    "How does perturbation shift community composition?",
                    "What condition restores beneficial microbial activity?",
                ],
            },
        },
    },
    "Chemistry": {
        "Organic chemistry": {
            "Reaction design": {
                "topics": [
                    "Catalyst screening",
                    "Reaction yield optimization",
                    "Stereoselective synthesis",
                ],
                "questions": [
                    "Which catalyst or solvent improves yield most?",
                    "How does reaction condition affect selectivity?",
                    "What mechanism explains byproduct formation?",
                ],
            },
            "Medicinal chemistry": {
                "topics": [
                    "Structure-activity relationships",
                    "Lead optimization",
                    "Drug-like property tuning",
                ],
                "questions": [
                    "Which structural feature improves target activity?",
                    "How can potency and solubility be balanced?",
                    "What modification reduces off-target risk?",
                ],
            },
        },
        "Materials chemistry": {
            "Energy materials": {
                "topics": [
                    "Battery electrolytes",
                    "Photocatalysts",
                    "Membrane materials",
                ],
                "questions": [
                    "Which composition improves stability or conductivity?",
                    "How does processing affect material performance?",
                    "What degradation mechanism limits lifetime?",
                ],
            },
            "Polymer chemistry": {
                "topics": [
                    "Biodegradable polymers",
                    "Conductive polymers",
                    "Polymer blends",
                ],
                "questions": [
                    "Which polymer property controls mechanical performance?",
                    "How does blend ratio affect conductivity or durability?",
                    "What formulation improves degradation behavior?",
                ],
            },
        },
    },
    "Earth and environmental science": {
        "Climate science": {
            "Climate adaptation": {
                "topics": [
                    "Heat resilience",
                    "Flood risk modeling",
                    "Drought forecasting",
                ],
                "questions": [
                    "Which local variable most predicts climate risk?",
                    "How does adaptation change vulnerability over time?",
                    "What early warning signal improves preparedness?",
                ],
            },
            "Atmospheric science": {
                "topics": [
                    "Aerosol effects",
                    "Extreme weather patterns",
                    "Urban heat islands",
                ],
                "questions": [
                    "Which atmospheric factor drives the observed pattern?",
                    "How do local conditions amplify extreme events?",
                    "What measurement improves short-term prediction?",
                ],
            },
        },
        "Environmental systems": {
            "Water systems": {
                "topics": [
                    "Water quality monitoring",
                    "Nutrient runoff",
                    "Groundwater recharge",
                ],
                "questions": [
                    "Which indicator detects water quality change earliest?",
                    "How does land use affect runoff or contamination?",
                    "What intervention improves water system recovery?",
                ],
            },
            "Conservation science": {
                "topics": [
                    "Biodiversity monitoring",
                    "Restoration ecology",
                    "Habitat connectivity",
                ],
                "questions": [
                    "Which monitoring method best detects biodiversity change?",
                    "How does restoration alter species richness?",
                    "What connectivity measure predicts population persistence?",
                ],
            },
        },
    },
    "Medicine and health": {
        "Clinical science": {
            "Diagnostics": {
                "topics": [
                    "Early detection biomarkers",
                    "Point-of-care testing",
                    "Risk stratification",
                ],
                "questions": [
                    "Which biomarker detects the condition earliest?",
                    "How accurate is a low-cost diagnostic workflow?",
                    "What risk score best predicts meaningful clinical change?",
                ],
            },
            "Therapeutics": {
                "topics": [
                    "Treatment response",
                    "Dose optimization",
                    "Adherence interventions",
                ],
                "questions": [
                    "Which factor predicts treatment response?",
                    "How can dose be optimized while limiting side effects?",
                    "What intervention improves adherence or outcomes?",
                ],
            },
        },
        "Public health": {
            "Epidemiology": {
                "topics": [
                    "Disease surveillance",
                    "Outbreak forecasting",
                    "Exposure risk",
                ],
                "questions": [
                    "Which exposure most changes disease risk?",
                    "How can surveillance detect outbreaks earlier?",
                    "What model improves forecasting under incomplete data?",
                ],
            },
            "Health behavior": {
                "topics": [
                    "Behavior change programs",
                    "Preventive care uptake",
                    "Community health interventions",
                ],
                "questions": [
                    "Which message or incentive changes behavior most?",
                    "How does context affect preventive care uptake?",
                    "What community intervention produces measurable impact?",
                ],
            },
        },
    },
    "Engineering": {
        "Mechanical engineering": {
            "Robotics and control": {
                "topics": [
                    "Adaptive control",
                    "Soft robotics",
                    "Human-robot interaction",
                ],
                "questions": [
                    "Which control strategy improves stability or precision?",
                    "How does material compliance affect task performance?",
                    "What interaction design reduces operator error?",
                ],
            },
            "Manufacturing": {
                "topics": [
                    "Additive manufacturing",
                    "Process monitoring",
                    "Quality control",
                ],
                "questions": [
                    "Which process parameter predicts defect formation?",
                    "How does monitoring improve yield or quality?",
                    "What design change reduces manufacturing variability?",
                ],
            },
        },
        "Electrical engineering": {
            "Signal processing": {
                "topics": [
                    "Sensor fusion",
                    "Noise reduction",
                    "Edge inference",
                ],
                "questions": [
                    "Which signal feature improves detection accuracy?",
                    "How does filtering affect useful information?",
                    "What edge method balances speed and reliability?",
                ],
            },
            "Energy systems": {
                "topics": [
                    "Grid resilience",
                    "Power electronics",
                    "Renewable integration",
                ],
                "questions": [
                    "Which control method improves grid stability?",
                    "How does storage change renewable reliability?",
                    "What failure mode limits system resilience?",
                ],
            },
        },
    },
    "Computer and information science": {
        "Artificial intelligence": {
            "Human-AI collaboration": {
                "topics": [
                    "Decision support",
                    "Trust calibration",
                    "AI-assisted research workflows",
                ],
                "questions": [
                    "Which workflow improves human decision quality?",
                    "How do explanations affect trust calibration?",
                    "What interaction reduces errors or uncertainty?",
                ],
            },
            "Machine learning robustness": {
                "topics": [
                    "Distribution shift",
                    "Model evaluation",
                    "Fairness auditing",
                ],
                "questions": [
                    "How robust is the model across datasets or groups?",
                    "Which metric best reveals failure under shift?",
                    "What intervention improves fairness or reliability?",
                ],
            },
        },
        "Data science": {
            "Scientific computing": {
                "topics": [
                    "Simulation workflows",
                    "Uncertainty quantification",
                    "Computational reproducibility",
                ],
                "questions": [
                    "Which simulation assumption most changes the result?",
                    "How can uncertainty be quantified and reduced?",
                    "What workflow improves reproducibility?",
                ],
            },
            "Privacy and security": {
                "topics": [
                    "Privacy-preserving analytics",
                    "Secure data sharing",
                    "Adversarial evaluation",
                ],
                "questions": [
                    "Which privacy method preserves the most utility?",
                    "How does data sharing affect risk and performance?",
                    "What threat model exposes the biggest weakness?",
                ],
            },
        },
    },
    "Mathematics": {
        "Applied mathematics": {
            "Dynamical systems": {
                "topics": [
                    "Stability analysis",
                    "Nonlinear dynamics",
                    "Control models",
                ],
                "questions": [
                    "Which parameter changes stability or convergence?",
                    "What mechanism produces nonlinear behavior?",
                    "How can control improve system behavior?",
                ],
            },
            "Optimization": {
                "topics": [
                    "Constrained optimization",
                    "Multi-objective optimization",
                    "Robust optimization",
                ],
                "questions": [
                    "Which objective tradeoff matters most?",
                    "How does constraint choice affect the solution?",
                    "What method improves robustness under uncertainty?",
                ],
            },
        },
        "Statistics": {
            "Experimental design": {
                "topics": [
                    "Power analysis",
                    "Causal inference",
                    "Bayesian experimental design",
                ],
                "questions": [
                    "Which design best detects the expected effect?",
                    "What assumption threatens causal interpretation?",
                    "How much data is needed for a credible result?",
                ],
            },
            "Modeling": {
                "topics": [
                    "Hierarchical models",
                    "Time series modeling",
                    "Uncertainty estimation",
                ],
                "questions": [
                    "Which model structure best captures variation?",
                    "How does uncertainty change the interpretation?",
                    "What predictor improves forecast quality?",
                ],
            },
        },
    },
    "Social and behavioral science": {
        "Psychology": {
            "Cognition and behavior": {
                "topics": [
                    "Decision-making",
                    "Attention and learning",
                    "Motivation",
                ],
                "questions": [
                    "Which factor changes behavior or decision quality?",
                    "How does attention affect learning outcomes?",
                    "What intervention improves motivation or persistence?",
                ],
            },
            "Health psychology": {
                "topics": [
                    "Risk perception",
                    "Behavior change",
                    "Stress and coping",
                ],
                "questions": [
                    "How does risk perception affect action?",
                    "Which intervention changes health behavior most?",
                    "What coping strategy improves measurable outcomes?",
                ],
            },
        },
        "Policy and education": {
            "Education research": {
                "topics": [
                    "Learning outcomes",
                    "Instructional design",
                    "Assessment feedback",
                ],
                "questions": [
                    "Which instructional method improves learning outcomes?",
                    "How does feedback timing affect performance?",
                    "What assessment predicts long-term retention?",
                ],
            },
            "Policy evaluation": {
                "topics": [
                    "Program impact",
                    "Implementation science",
                    "Equity analysis",
                ],
                "questions": [
                    "Which policy produces measurable impact?",
                    "How does implementation context affect outcomes?",
                    "What equity metric best captures program effects?",
                ],
            },
        },
    },
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
    return list(SCIENCE_TREE.keys())


def discipline_names(branch: str) -> list[str]:
    return list(SCIENCE_TREE.get(branch, {}).keys())


def subfield_names(branch: str, discipline: str) -> list[str]:
    return list(SCIENCE_TREE.get(branch, {}).get(discipline, {}).keys())


def topics_for_path(branch: str, discipline: str, subfield: str) -> list[str]:
    node = _path_node(branch, discipline, subfield)
    return list(node.get("topics", []))


def questions_for_path(branch: str, discipline: str, subfield: str) -> list[str]:
    node = _path_node(branch, discipline, subfield)
    return list(node.get("questions", []))


def topics_for_branch(branch: str) -> list[str]:
    topics: list[str] = []
    for discipline in discipline_names(branch):
        for subfield in subfield_names(branch, discipline):
            topics.extend(topics_for_path(branch, discipline, subfield))
    return topics


def questions_for_branch(branch: str) -> list[str]:
    questions: list[str] = []
    for discipline in discipline_names(branch):
        for subfield in subfield_names(branch, discipline):
            questions.extend(questions_for_path(branch, discipline, subfield))
    return questions


def path_label(branch: str, discipline: str, subfield: str) -> str:
    return f"{branch} > {discipline} > {subfield}"


def default_path() -> tuple[str, str, str]:
    branch = branch_names()[0]
    discipline = discipline_names(branch)[0]
    subfield = subfield_names(branch, discipline)[0]
    return branch, discipline, subfield


def _path_node(branch: str, discipline: str, subfield: str) -> dict[str, Any]:
    return SCIENCE_TREE.get(branch, {}).get(discipline, {}).get(subfield, {})
