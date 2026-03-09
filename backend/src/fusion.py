"""
fusion.py
=========
Fusione Inverse-Variance Weighting (IVW) delle tre sorgenti.

Schema pesi — letti da .env tramite config.py
─────────────────────────────────────────────────────────────────────
SERVER ONLINE  (V2I_receiver attivo):
    V2I_receiver    → W_SERVER    (default 0.60)
    camera_frontale → W_FRONTALE  (default 0.30)
    camera_laterale → W_LATERALE  (default 0.10)

    confidence_fusa = (P_server × 0.60) + (P_front × 0.30) + (P_lat × 0.10)

SERVER OFFLINE (V2I_receiver = null):
    camera_frontale → W_FRONTALE_OFFLINE  (default 0.75)
    camera_laterale → W_LATERALE_OFFLINE  (default 0.25)
─────────────────────────────────────────────────────────────────────

Se un sensore dello schema attivo è offline, il suo peso viene
redistribuito proporzionalmente agli altri sensori attivi.

Se TUTTI i sensori sono offline → FusionResult(fused_text="NO_DATA", confidence=0.0)
"""

from dataclasses import dataclass, field
from src.config import (
    W_SERVER, W_FRONTALE, W_LATERALE,
    W_FRONTALE_OFFLINE, W_LATERALE_OFFLINE,
)


@dataclass
class FusionResult:
    fused_text:        str    # testo vincitore
    fusion_confidence: float  # confidence IVW in [0, 1]
    server_online:     bool   # True se V2I_receiver era attivo
    active_sensors:    list[str] = field(default_factory=list)
    evidence:          dict      = field(default_factory=dict)


def fuse_readings(normalized_sensors: dict[str, dict | None]) -> FusionResult:
    """
    Fonde le letture normalizzate con IVW.

    Args:
        normalized_sensors: {nome_sensore: {"testo": str, "confidenza": float} | None}

    Returns:
        FusionResult con fused_text e fusion_confidence.

    Algoritmo:
        1. Controlla se V2I_receiver è online → sceglie schema pesi.
        2. Per i sensori dello schema attivo e online calcola:
               contributo_i = peso_normalizzato_i × confidenza_i
        3. Accumula i contributi per testo unico.
        4. Il testo con contributo totale massimo → fused_text.
        5. fusion_confidence = contributo totale del testo vincitore.
    """
    v2i_reading = normalized_sensors.get("V2I_receiver")
    server_online = bool(v2i_reading and v2i_reading.get("testo"))

    # Schema pesi in base allo stato del server
    if server_online:
        weight_schema: dict[str, float] = {
            "V2I_receiver":    W_SERVER,
            "camera_frontale": W_FRONTALE,
            "camera_laterale": W_LATERALE,
        }
    else:
        weight_schema = {
            "camera_frontale": W_FRONTALE_OFFLINE,
            "camera_laterale": W_LATERALE_OFFLINE,
        }

    # Filtra sensori attivi tra quelli dello schema
    active: dict[str, dict] = {
        name: normalized_sensors[name]
        for name in weight_schema
        if normalized_sensors.get(name) and normalized_sensors[name].get("testo")
    }

    if not active:
        return FusionResult(
            fused_text="NO_DATA",
            fusion_confidence=0.0,
            server_online=server_online,
        )

    # Normalizza pesi sui soli sensori attivi
    raw_w = {s: weight_schema[s] for s in active}
    total = sum(raw_w.values())
    norm_w = {s: w / total for s, w in raw_w.items()}

    # Accumula contributi per testo
    text_scores: dict[str, float] = {}
    evidence: dict[str, dict] = {}

    for name, reading in active.items():
        text = reading["testo"]
        conf = float(reading.get("confidenza", 1.0))
        contrib = norm_w[name] * conf
        text_scores[text] = text_scores.get(text, 0.0) + contrib
        evidence[name] = {
            "testo":      text,
            "confidenza": round(conf, 3),
            "peso":       round(norm_w[name], 3),
            "contributo": round(contrib, 3),
        }

    best_text = max(text_scores, key=lambda t: text_scores[t])
    best_conf = round(min(text_scores[best_text], 1.0), 4)

    return FusionResult(
        fused_text=best_text,
        fusion_confidence=best_conf,
        server_online=server_online,
        active_sensors=list(active.keys()),
        evidence=evidence,
    )