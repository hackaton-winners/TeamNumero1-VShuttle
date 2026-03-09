"""
decision.py
===========
Motore decisionale: mappa confidence IVW + ParsedMeaning → azione + reason.

Soglie (da config.py / .env):
────────────────────────────────────────────────────────────────────
  THRESHOLD_CERTAIN   (default 0.75) — sopra: GO o STOP definitivo
  THRESHOLD_UNCERTAIN (default 0.50) — sotto: sempre HUMAN_CONFIRM

  Zona certa    → conf >= THRESHOLD_CERTAIN  → GO o STOP
  Zona grigia   → THRESHOLD_UNCERTAIN <= conf < THRESHOLD_CERTAIN → HUMAN_CONFIRM
  Zona rumore   → conf < THRESHOLD_UNCERTAIN → HUMAN_CONFIRM
────────────────────────────────────────────────────────────────────

Priorità decisionale:
  1. NO_DATA                                     → HUMAN_CONFIRM
  2. Restrizione attiva + eccezione navette/bus  → GO  (sempre)
  3. conf < THRESHOLD_CERTAIN                    → HUMAN_CONFIRM
  4. Accesso libero esplicito (GO/LIBERO/…)      → GO
  5. Restrizione attiva senza eccezioni          → STOP
  6. Restrizione fuori orario                    → GO
  7. Nessuna restrizione                         → GO
"""

from dataclasses import dataclass
from src.parser import ParsedMeaning
from src.config import THRESHOLD_CERTAIN, THRESHOLD_UNCERTAIN


@dataclass
class DecisionResult:
    action:     str    # "GO" | "STOP" | "HUMAN_CONFIRM"
    confidence: float  # confidence IVW (0.0 – 1.0)
    reason:     str    # spiegazione human-readable da inviare al frontend


def decide(
    meaning: ParsedMeaning,
    fusion_confidence: float,
    fused_text: str,
) -> DecisionResult:
    """
    Determina GO / STOP / HUMAN_CONFIRM con relativa reason.

    Args:
        meaning           : output del parser semantico.
        fusion_confidence : confidence IVW dalla fusione sensoriale.
        fused_text        : testo fuso (necessario per check NO_DATA).

    Returns:
        DecisionResult con action, confidence e reason.
    """
    conf = round(fusion_confidence, 4)

    def result(action: str, reason: str) -> DecisionResult:
        return DecisionResult(action=action, confidence=conf, reason=reason)

    # ── 1. Nessun dato ───────────────────────────────────────────────── #
    if fused_text == "NO_DATA":
        return result(
            "HUMAN_CONFIRM",
            "Nessun sensore attivo: stato della zona non determinabile.",
        )

    # ── 2. Eccezione navette/bus → GO incondizionato ──────────────────── #
    if meaning.has_restriction and meaning.restriction_active and meaning.has_exception:
        return result(
            "GO",
            f"Zona riservata ({meaning.matched_restriction}) con eccezione "
            f"'{meaning.matched_exception}': navetta autorizzata al transito.",
        )

    # ── 3. Confidenza insufficiente → HUMAN_CONFIRM ───────────────────── #
    if conf < THRESHOLD_CERTAIN:
        if conf < THRESHOLD_UNCERTAIN:
            reason_detail = f"segnale troppo debole (conf={conf:.0%})"
        else:
            reason_detail = f"confidenza in zona grigia (conf={conf:.0%})"
        return result(
            "HUMAN_CONFIRM",
            f"Lettura ambigua — {reason_detail}. Richiesto controllo umano.",
        )

    # Da qui: conf >= THRESHOLD_CERTAIN → decisione certa

    # ── 4. Accesso libero esplicito ───────────────────────────────────── #
    if meaning.is_free and not meaning.has_restriction:
        return result(
            "GO",
            f"Accesso libero rilevato con alta confidenza ({conf:.0%}).",
        )

    # ── 5. Restrizione attiva, nessuna eccezione ──────────────────────── #
    if meaning.has_restriction and meaning.restriction_active:
        return result(
            "STOP",
            f"Zona '{meaning.matched_restriction}' attiva: transito vietato "
            f"(conf={conf:.0%}).",
        )

    # ── 6. Restrizione presente ma fuori orario ───────────────────────── #
    if meaning.has_restriction and not meaning.restriction_active:
        tw = meaning.time_window
        window_str = f"{tw[0]}-{tw[1]}" if tw else "N/D"
        return result(
            "GO",
            f"Zona '{meaning.matched_restriction}' non attiva all'orario rilevato "
            f"(finestra {window_str}): transito consentito.",
        )

    # ── 7. Nessuna restrizione ────────────────────────────────────────── #
    return result(
        "GO",
        f"Nessuna restrizione rilevata (conf={conf:.0%}): transito libero.",
    )