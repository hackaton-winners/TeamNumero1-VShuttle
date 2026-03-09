"""
parser.py
=========
Parser semantico: interpreta il testo fuso e il contesto orario/giornaliero.

Estrae:
  - Presenza di restrizione (ZTL, DIVIETO, STOP…)
  - Presenza di eccezione per navette/bus
  - Se la restrizione è attualmente attiva (finestra oraria + giorno)
  - Se il testo indica accesso libero

Come estendere:
  - RESTRICTION_KEYWORDS : nuove parole che significano divieto
  - EXCEPTION_KEYWORDS   : nuove varianti per "eccetto navette/bus"
  - FREE_KEYWORDS         : nuovi testi che indicano libero accesso
"""

import re
from dataclasses import dataclass, field


RESTRICTION_KEYWORDS: list[str] = [
    "ZTL", "DIVIETO", "STOP", "VIETATO", "CHIUSO", "BLOCKED",
]

EXCEPTION_KEYWORDS: list[str] = [
    "ECCETTO NAVETTE L4", "ECCETTO NAVETTE", "ECCETTO NAVETTA",
    "ECCETTO BUS", "ESCLUSO NAVETTE", "ESCLUSO BUS",
    "AUTORIZZATO", "NAVETTE",
]

FREE_KEYWORDS: list[str] = [
    "GO", "LIBERO", "APERTO", "ACCESSO LIBERO",
]


@dataclass
class ParsedMeaning:
    has_restriction:     bool = False
    has_exception:       bool = False
    restriction_active:  bool = False
    is_free:             bool = False
    time_window:         tuple[int, int] | None = None
    matched_restriction: str = ""
    matched_exception:   str = ""
    notes:               list[str] = field(default_factory=list)


def _parse_time_window(text: str) -> tuple[int, int] | None:
    """Estrae (ora_inizio, ora_fine) dal testo, es. '7-20' o '07:00-20:00'."""
    m = re.search(r"(\d{1,2})(?::\d{2})?\s*[-–]\s*(\d{1,2})(?::\d{2})?", text)
    if m:
        s, e = int(m.group(1)), int(m.group(2))
        if 0 <= s <= 23 and 0 <= e <= 23:
            return s, e
    return None


def _parse_hour(orario: str) -> int | None:
    """Converte 'HH:MM' in ora intera."""
    m = re.match(r"(\d{1,2}):\d{2}", orario.strip())
    return int(m.group(1)) if m else None


def parse_meaning(fused_text: str, orario: str, giorno: str) -> ParsedMeaning:
    """
    Analizza testo fuso e contesto temporale.

    Args:
        fused_text : testo normalizzato e fuso.
        orario     : stringa "HH:MM".
        giorno     : nome giorno italiano.

    Returns:
        ParsedMeaning con tutti i flag popolati.
    """
    result = ParsedMeaning()
    text = fused_text.upper()

    # Accesso libero esplicito
    for kw in FREE_KEYWORDS:
        if kw in text:
            result.is_free = True
            result.notes.append(f"Accesso libero: '{kw}'")
            break

    # Restrizione
    for kw in RESTRICTION_KEYWORDS:
        if kw in text:
            result.has_restriction = True
            result.matched_restriction = kw
            result.notes.append(f"Restrizione: '{kw}'")
            break

    # Eccezione navette (controlla prima le frasi più lunghe)
    if result.has_restriction:
        for kw in sorted(EXCEPTION_KEYWORDS, key=len, reverse=True):
            if kw in text:
                result.has_exception = True
                result.matched_exception = kw
                result.notes.append(f"Eccezione: '{kw}'")
                break

    # Finestra oraria
    tw = _parse_time_window(text)
    current_h = _parse_hour(orario)

    if tw:
        result.time_window = tw
        s, e = tw
        if current_h is not None:
            result.restriction_active = s <= current_h < e
            result.notes.append(
                f"Orario {orario} {'dentro' if result.restriction_active else 'fuori'} finestra {s}-{e}"
            )
        else:
            result.restriction_active = True   # fail-safe: assumiamo attiva
            result.notes.append("Orario non parsabile → restrizione assunta attiva")
    elif result.has_restriction:
        result.restriction_active = True        # nessuna finestra → H24
        result.notes.append("Nessuna finestra oraria → restrizione H24")

    return result