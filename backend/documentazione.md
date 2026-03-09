
Inverse-Variance Weighting

se server online:

Fonte,Tipo,Affidabilità (Confidenza),Peso Suggerito (w)
Server,Gold Standard,95% - 99%,wa​=0.60 (60%)
Sensore Frontale,Hardware High-End,85% - 90%,wb​=0.30 (30%)
Sensore Laterale,Hardware Mid-Range,60% - 70%,wc​=0.10 (10%)

Valore Finale=(Pserver​⋅0.6)+(Pfront​⋅0.3)+(Plat​⋅0.1)

se server offline:

frontale = 0.75
laterale = 0.25



backend/
│
├── requirements.txt      ← dipendenze runtime (Flask, Flask-CORS)
├── requirements-dev.txt  ← dipendenze dev (pytest)
├── main.py               ← entry point (batch e API Flask)
│
├── data/
│   ├── input.json        ← scenari di input da processare
│   └── output.json       ← risultati generati (creato dopo il primo run)
│
├── src/
│   ├── __init__.py
│   ├── config.py         ← legge .env e espone i parametri
│   ├── normalize.py      ← normalizzazione testo OCR
│   ├── fusion.py         ← fusione IVW dei tre sensori
│   ├── parser.py         ← parsing semantico (ZTL, orari, eccezioni)
│   ├── decision.py       ← logica GO / STOP / HUMAN_CONFIRM + reason
│   └── pipeline.py       ← orchestratore: carica JSON → produce lista
│
└── tests/
    ├── __init__.py
    └── test_all.py       ← 53 test (normalize, fusion, parser, decision, pipeline)