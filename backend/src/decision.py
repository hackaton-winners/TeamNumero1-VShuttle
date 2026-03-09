"""
decision.py
===========
Motore decisionale: mappa confidence IVW + ParsedMeaning → azione + reason.

Soglie (da config.py / .env):
────────────────────────────────────────────────────────────────────
  THRESHOLD_CERTAIN   (default 0.75) — sopra: GO o STOP definitivo
  THRESHOLD_UNCERTAIN (default 0.50) — sotto: rumore puro, HUMAN_CONFIRM
                                        blocca anche l'eccezione navette

  Zona certa   → conf >= THRESHOLD_CERTAIN                        → GO o STOP
  Zona grigia  → THRESHOLD_UNCERTAIN <= conf < THRESHOLD_CERTAIN  → HUMAN_CONFIRM
                 (eccetto se ha_exception → GO, navetta autorizzata)
  Zona rumore  → conf < THRESHOLD_UNCERTAIN                       → HUMAN_CONFIRM sempre
────────────────────────────────────────────────────────────────────

Priorità decisionale:
  1. NO_DATA                                              → HUMAN_CONFIRM
  2. conf < THRESHOLD_UNCERTAIN  (rumore puro)           → HUMAN_CONFIRM
         ↑ blocca tutto, eccezione navette inclusa:
           se il segnale è troppo debole non possiamo fidarci
           nemmeno del testo "ECCETTO NAVETTE"
  3. Restrizione attiva + eccezione navette/bus
     + conf >= THRESHOLD_UNCERTAIN                        → GO
         ↑ la navetta è autorizzata ma serve almeno un segnale
           minimamente leggibile (sopra la soglia del rumore)
  4. conf < THRESHOLD_CERTAIN  (zona grigia)             → HUMAN_CONFIRM
  5. Accesso libero esplicito (GO/LIBERO/…)              → GO
  6. Restrizione attiva senza eccezioni                  → STOP
  7. Restrizione fuori orario                            → GO
  8. Nessuna restrizione                                 → GO

Perché la soglia dell'eccezione è THRESHOLD_UNCERTAIN e non THRESHOLD_CERTAIN?
  L'eccezione navette ha semantica diversa dagli altri casi: non stiamo
  decidendo se la zona è vietata o libera (dove serve alta certezza), ma
  stiamo riconoscendo che la navetta è per definizione autorizzata.
  Bastano quindi segnali "sopra il rumore" per riconoscere l'eccezione.
  Con conf < THRESHOLD_UNCERTAIN il testo è troppo corrotto per essere
  affidabile: potremmo aver letto "ECCETTO NAVETTE" su un cartello che
  in realtà diceva altro → HUMAN_CONFIRM è la scelta sicura.
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

    # ── 2. Rumore puro: segnale troppo debole per qualsiasi decisione ─── #
    # Questo blocco viene PRIMA dell'eccezione navette: se la confidenza è
    # sotto THRESHOLD_UNCERTAIN non possiamo fidarci nemmeno del testo
    # "ECCETTO NAVETTE" — potrebbe essere un falso positivo OCR.
    if conf < THRESHOLD_UNCERTAIN:
        return result(
            "HUMAN_CONFIRM",
            f"Segnale troppo debole (conf={conf:.0%}): lettura inaffidabile. "
            f"Richiesto controllo umano.",
        )

    # ── 3. Eccezione navette/bus (conf >= THRESHOLD_UNCERTAIN) ─────────── #
    # La navetta è per definizione autorizzata nelle zone con eccezione.
    # Basta essere sopra la soglia del rumore per riconoscere l'eccezione,
    # non serve la certezza piena richiesta per GO/STOP generici.
    if meaning.has_restriction and meaning.restriction_active and meaning.has_exception:
        return result(
            "GO",
            f"Zona riservata ({meaning.matched_restriction}) con eccezione "
            f"'{meaning.matched_exception}': navetta autorizzata al transito "
            f"(conf={conf:.0%}).",
        )

    # ── 4. Zona grigia: sopra il rumore ma sotto la certezza ──────────── #
    if conf < THRESHOLD_CERTAIN:
        return result(
            "HUMAN_CONFIRM",
            f"Confidenza in zona grigia (conf={conf:.0%}): lettura ambigua. "
            f"Richiesto controllo umano.",
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