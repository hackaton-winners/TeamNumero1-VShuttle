"""
pipeline.py
===========
Orchestratore: legge input.json e produce la lista di risultati.

Output per ogni scenario (elemento della lista):
    {
        "id_scenario": int,
        "action":      "GO" | "STOP" | "HUMAN_CONFIRM",
        "confidence":  float,   # confidence IVW in [0.0, 1.0]
        "reason":      str      # spiegazione per il frontend
    }

Flusso interno per scenario:
    validate → normalize → fuse (IVW) → parse → decide

Fail-safe: errori imprevisti producono HUMAN_CONFIRM senza bloccare
           l'elaborazione degli altri scenari.
"""

import json
import traceback
from pathlib import Path

from src.config import INPUT_JSON_PATH
from src.normalize import normalize_text
from src.fusion import fuse_readings
from src.parser import parse_meaning
from src.decision import decide


# ---------------------------------------------------------------------------
# Validazione
# ---------------------------------------------------------------------------

def _validate(scenario: dict) -> list[str]:
    errors = []
    for field in ["id_scenario", "sensori", "orario_rilevamento", "giorno_settimana"]:
        if field not in scenario:
            errors.append(f"campo mancante: '{field}'")
    if "sensori" in scenario:
        missing = {"camera_frontale", "camera_laterale", "V2I_receiver"} - set(scenario["sensori"])
        if missing:
            errors.append(f"sensori mancanti: {missing}")
    return errors


# ---------------------------------------------------------------------------
# Elaborazione singolo scenario
# ---------------------------------------------------------------------------

def process_scenario(scenario: dict) -> dict:
    """
    Processa uno scenario e restituisce l'elemento da aggiungere alla lista.

    Returns:
        {"id_scenario": int, "action": str, "confidence": float, "reason": str}
    """
    id_scenario = scenario.get("id_scenario", -1)

    try:
        errors = _validate(scenario)
        if errors:
            return _fail_safe(id_scenario, f"Input non valido: {'; '.join(errors)}")

        # STEP 1 — Normalizzazione OCR
        normalized: dict[str, dict | None] = {}
        for name, reading in scenario["sensori"].items():
            if reading is None:
                normalized[name] = None
            else:
                normalized[name] = {
                    "testo":      normalize_text(reading.get("testo")),
                    "confidenza": reading.get("confidenza", 0.0),
                }

        # STEP 2 — Fusione IVW
        fusion = fuse_readings(normalized)

        # STEP 3 — Parsing semantico
        meaning = parse_meaning(
            fused_text=fusion.fused_text,
            orario=scenario["orario_rilevamento"],
            giorno=scenario["giorno_settimana"],
        )

        # STEP 4 — Decisione
        decision = decide(
            meaning=meaning,
            fusion_confidence=fusion.fusion_confidence,
            fused_text=fusion.fused_text,
        )

        return {
            "id_scenario": id_scenario,
            "action":      decision.action,
            "confidence":  decision.confidence,
            "reason":      decision.reason,
        }

    except Exception as exc:  # noqa: BLE001
        tb = traceback.format_exc()
        return _fail_safe(id_scenario, f"Errore imprevisto: {exc}\n{tb}")


def _fail_safe(id_scenario: int, detail: str) -> dict:
    return {
        "id_scenario": id_scenario,
        "action":      "HUMAN_CONFIRM",
        "confidence":  0.0,
        "reason":      f"[FAIL-SAFE] {detail}",
    }


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def run_batch(input_path: Path | None = None) -> list[dict]:
    """
    Carica input.json (o il path passato) e restituisce la lista completa.

    Returns:
        Lista di dict {"id_scenario", "action", "confidence", "reason"}.
    """
    path = input_path or INPUT_JSON_PATH

    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    return [process_scenario(s) for s in data]