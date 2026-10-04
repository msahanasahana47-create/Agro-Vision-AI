"""Advisory treatment dictionary for plant diseases.

Non-negotiable rule:
All recommendations must carry the mandatory disclaimer:
'advisory, consult a local agricultural officer'.
"""

DISCLAIMER = "Advisory only. Always consult a local agricultural officer or certified agronomist before taking chemical or agronomic action."

TREATMENTS = {
    "healthy": {
        "disease_name": "Healthy Plant",
        "symptoms": "Foliage shows vibrant color, uniform growth, and no signs of lesions, wilting, or fungal sporulation.",
        "organic_control": "Maintain balanced organic fertilization, optimal drip irrigation, and routine crop scouting.",
        "chemical_control": "None required.",
        "prevention": "Crop rotation, sanitized farming implements, and disease-resistant cultivars.",
        "needs_source_verification": False,
        "disclaimer": DISCLAIMER,
    },
    "default_unknown": {
        "disease_name": "Unidentified Foliar Anomaly",
        "symptoms": "Leaf features atypical spotting or discoloration.",
        "organic_control": "Isolate affected specimens, avoid overhead sprinkling, apply organic neem extract spray.",
        "chemical_control": "Consult local extension officer for physical leaf sample testing before chemical application.",
        "prevention": "Ensure field drainage and proper plant spacing for aeration.",
        "needs_source_verification": True,
        "disclaimer": DISCLAIMER,
    }
}


def get_treatment_advice(class_name: str) -> dict:
    """Retrieve advisory treatment guidance for a predicted disease class."""
    key = class_name.lower().strip()
    advice = TREATMENTS.get(key, TREATMENTS.get("default_unknown")).copy()
    advice["disclaimer"] = DISCLAIMER
    return advice
