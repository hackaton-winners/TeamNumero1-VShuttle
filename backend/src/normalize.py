"""
normalize.py
============
Normalizzazione del testo grezzo proveniente dai sensori OCR.

Converte testo rumoroso (errori di cifre/lettere tipici dell'OCR) in forme
canoniche riconoscibili dal parser semantico.

Come estendere:
  - OCR_FIXES   : aggiungere tuple (pattern_regex, sostituzione)
  - SYNONYM_MAP : aggiungere alias per testi equivalenti
"""

import re

# ---------------------------------------------------------------------------
# Correzioni OCR — applicate nell'ordine della lista
# Ogni elemento è (pattern_regex, sostituzione).
# ---------------------------------------------------------------------------
OCR_FIXES: list[tuple[str, str]] = [
    (r"0", "O"),                               # zero → O
    (r"1", "I"),                               # uno  → I
    (r"5", "S"),                               # cinque → S
    (r"3", "E"),                               # tre → E
    (r"8", "B"),                               # otto → B
    (r"\bD[I1]V[I1]ET[O0]\b",  "DIVIETO"),
    (r"\bTRANS[I1]T[O0]\b",    "TRANSITO"),
    (r"\bNAVETT[E3]\b",        "NAVETTE"),
    (r"\bECC[E3]TT[O0]\b",     "ECCETTO"),
    (r"\bC[O0]NS[E3]NT[I1]T[O0]\b", "CONSENTITO"),
    (r"\bACC[E3]SS[O0]\b",     "ACCESSO"),
]

# ---------------------------------------------------------------------------
# Sinonimi — normalizza varianti semanticamente equivalenti
# Le frasi più lunghe vengono controllate per prime.
# ---------------------------------------------------------------------------
SYNONYM_MAP: dict[str, str] = {
    "ACCESSO CONSENTITO": "GO",
    "LIBERO TRANSITO":    "GO",
    "TRANSITO LIBERO":    "GO",
    "VIA LIBERA":         "GO",
    "LIBERO":             "GO",
    "DIVIETO DI TRANSITO": "DIVIETO",
    "DIVIETO TRANSITO":    "DIVIETO",
    "VIETATO":             "DIVIETO",
}


def normalize_text(raw: str | None) -> str:
    """
    Normalizza un testo grezzo del sensore.

    Passi:
      1. None / vuoto → stringa vuota
      2. Uppercase + strip
      3. Rimozione simboli non alfanumerici (eccetto spazi e trattini)
      4. Correzioni OCR
      5. Sostituzione sinonimi (frasi più lunghe prima)
      6. Collasso spazi multipli

    Returns:
        Stringa normalizzata in uppercase.
    """
    if not raw:
        return ""

    text = raw.upper().strip()
    text = re.sub(r"[^A-Z0-9\s\-]", " ", text)

    for pattern, replacement in OCR_FIXES:
        text = re.sub(pattern, replacement, text)

    text = re.sub(r"\s+", " ", text).strip()

    for phrase in sorted(SYNONYM_MAP, key=len, reverse=True):
        if phrase in text:
            text = text.replace(phrase, SYNONYM_MAP[phrase])

    return text.strip()