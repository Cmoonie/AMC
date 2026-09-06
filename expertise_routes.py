"""
expertise_routes.py — Centrale mapping van expertise labels naar pagina's.
Importeer dit in app.py, onderzoeker.py en kennisgraaf.py.

Gebruik:
    from expertise_routes import uitgewerkte_expertise, pagina_namen
"""

uitgewerkte_expertise = {
    # Robert
    "methotrexate": "pages/expertise_methotrexaat.py",
    "methotrexaat": "pages/expertise_methotrexaat.py",
    "methotrexate polyglutamates": "pages/expertise_methotrexaat.py",
    "methotrexate polyglutamate": "pages/expertise_methotrexaat.py",
    "gene expression": "pages/expertise_gene_expression.py",
    "laboratory medicine": "pages/expertise_laboratorium_diagnostiek.py",
    # Sjors
    "neurofilament light chain": "pages/expertise_neurofilament.py",
    "amyloid beta": "pages/expertise_amyloid.py",
    "systemic amyloidosis": "pages/expertise_amyloid.py",
    "attrv amyloidosis": "pages/expertise_amyloid.py",
    # Martijn
    "clinical decision making": "pages/expertise_clinical_decision.py",
    "clinical prediction models": "pages/expertise_clinical_decision.py",
    "epidemiology": "pages/expertise_epidemiology.py",
    "clinical practice guidelines": "pages/expertise_clinical_decision.py",
    "alzheimer": "pages/expertise_amyloid.py",
}

# Mooie namen voor de knoppen
pagina_namen = {
    "pages/expertise_methotrexaat.py": "Methotrexaat",
    "pages/expertise_gene_expression.py": "Gene Expression",
    "pages/expertise_laboratorium_diagnostiek.py": "Laboratorium Diagnostiek",
    "pages/expertise_neurofilament.py": "Neurofilament Light Chain",
    "pages/expertise_amyloid.py": "Amyloid Beta",
    "pages/expertise_clinical_decision.py": "Clinical Decision Making",
    "pages/expertise_epidemiology.py": "Epidemiologie",
}