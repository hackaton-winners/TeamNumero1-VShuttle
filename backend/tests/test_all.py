"""
tests/test_all.py
=================
Suite di test per tutti i moduli.

Esecuzione:
    cd shuttle_v3
    python tests/test_all.py
    # oppure, se pytest disponibile:
    python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_passed = 0
_failed: list[str] = []


def check(name: str, cond: bool) -> None:
    global _passed
    if cond:
        print(f"  ✓ {name}")
        _passed += 1
    else:
        _failed.append(name)
        print(f"  ✗ {name}")


# =============================================================================
# NORMALIZE
# =============================================================================
print("\n=== normalize ===")
from src.normalize import normalize_text

check("None → ''",                    normalize_text(None) == "")
check("vuoto → ''",                   normalize_text("") == "")
check("lowercase → uppercase",        normalize_text("ztl") == "ZTL")
check("OCR D1V1ET0 → DIVIETO",        "DIVIETO" in normalize_text("D1V1ET0"))
check("OCR D1V1ET0 DI TRANS1T0",      "DIVIETO" in normalize_text("D1V1ET0 D1 TRANS1T0"))
check("LIBERO TRANSITO → GO",         normalize_text("LIBERO TRANSITO") == "GO")
check("ACCESSO CONSENTITO → GO",      normalize_text("ACCESSO CONSENTITO") == "GO")
check("ZTL rimane ZTL",               normalize_text("ZTL") == "ZTL")
check("ZTL ECCETTO NAVETTE conserva", "ECCETTO NAVETTE" in normalize_text("ZTL ECCETTO NAVETTE"))


# =============================================================================
# FUSION
# =============================================================================
print("\n=== fusion ===")
from src.fusion import fuse_readings

def sens(f=None, l=None, v=None):
    def r(t, c): return {"testo": t, "confidenza": c}
    return {
        "camera_frontale": r(*f) if f else None,
        "camera_laterale": r(*l) if l else None,
        "V2I_receiver":    r(*v) if v else None,
    }

res = fuse_readings(sens())
check("tutti null → NO_DATA",          res.fused_text == "NO_DATA")
check("tutti null → conf=0.0",         res.fusion_confidence == 0.0)
check("tutti null → server_online=F",  res.server_online is False)

res = fuse_readings(sens(f=("ZTL", 0.9), l=("ZTL", 0.85), v=("ZTL", 0.97)))
check("tutti concordi → ZTL",          res.fused_text == "ZTL")
check("tutti concordi → conf > 0.9",   res.fusion_confidence > 0.9)
check("server online → True",          res.server_online is True)
check("conf ≤ 1.0",                    res.fusion_confidence <= 1.0)

# Server offline: solo frontale e laterale
res = fuse_readings(sens(f=("ZTL", 0.90), l=("ZTL", 0.85)))
check("server offline → False",        res.server_online is False)
check("server offline → fused ZTL",    res.fused_text == "ZTL")
# conf = 0.75*0.90 + 0.25*0.85 = 0.675+0.2125 = 0.8875
check("server offline conf ≈ 0.8875",  abs(res.fusion_confidence - 0.8875) < 0.001)

# Server online con pesi: solo frontale attiva
res = fuse_readings(sens(f=("DIVIETO", 0.88), v=("DIVIETO", 0.95)))
check("V2I+frontale, no lat",          res.fused_text == "DIVIETO")


# =============================================================================
# PARSER
# =============================================================================
print("\n=== parser ===")
from src.parser import parse_meaning

m = parse_meaning("ZTL", "09:00", "Lunedì")
check("ZTL → has_restriction",         m.has_restriction)
check("ZTL → restriction_active H24",  m.restriction_active)

m = parse_meaning("ZTL ECCETTO NAVETTE", "09:00", "Lunedì")
check("ECCETTO NAVETTE → has_exception", m.has_exception)

m = parse_meaning("ZTL ECCETTO BUS", "10:00", "Martedì")
check("ECCETTO BUS → has_exception",   m.has_exception)

m = parse_meaning("ZTL ORARIO 7-20", "21:00", "Lunedì")
check("ZTL fuori finestra → not active", not m.restriction_active)

m = parse_meaning("ZTL ORARIO 7-20", "09:00", "Lunedì")
check("ZTL dentro finestra → active",  m.restriction_active)

m = parse_meaning("GO", "12:00", "Mercoledì")
check("GO → is_free",                  m.is_free)

m = parse_meaning("NO_DATA", "09:00", "Lunedì")
check("NO_DATA → no restriction",      not m.has_restriction)
check("NO_DATA → not free",            not m.is_free)


# =============================================================================
# DECISION
# =============================================================================
print("\n=== decision ===")
from src.decision import decide
from src.parser import ParsedMeaning

def mkm(**kw):
    d = dict(has_restriction=False, has_exception=False, restriction_active=False,
             is_free=False, time_window=None, matched_restriction="",
             matched_exception="", notes=[])
    d.update(kw)
    return ParsedMeaning(**d)

r = decide(mkm(), 0.0, "NO_DATA")
check("NO_DATA → HUMAN_CONFIRM",       r.action == "HUMAN_CONFIRM")
check("NO_DATA reason non vuota",      len(r.reason) > 0)

r = decide(mkm(is_free=True), 0.85, "GO")
check("GO libero alta conf → GO",      r.action == "GO")

r = decide(mkm(is_free=True), 0.60, "GO")
check("GO libero bassa conf → HC",     r.action == "HUMAN_CONFIRM")

r = decide(mkm(has_restriction=True, restriction_active=True, matched_restriction="ZTL"), 0.90, "ZTL")
check("ZTL attiva alta conf → STOP",   r.action == "STOP")

r = decide(mkm(has_restriction=True, restriction_active=True, matched_restriction="ZTL"), 0.60, "ZTL")
check("ZTL attiva bassa conf → HC",    r.action == "HUMAN_CONFIRM")

r = decide(mkm(has_restriction=True, restriction_active=True, has_exception=True,
               matched_restriction="ZTL", matched_exception="ECCETTO NAVETTE"), 0.95, "ZTL ECCETTO NAVETTE")
check("ZTL + eccezione → GO",          r.action == "GO")

r = decide(mkm(has_restriction=True, restriction_active=True, has_exception=True,
               matched_restriction="ZTL", matched_exception="ECCETTO NAVETTE"), 0.40, "ZTL ECCETTO NAVETTE")
check("ZTL + eccezione sotto THRESHOLD_UNCERTAIN (0.40) -> HUMAN_CONFIRM", r.action == "HUMAN_CONFIRM")

r = decide(mkm(has_restriction=True, restriction_active=True, has_exception=True,
               matched_restriction="ZTL", matched_exception="ECCETTO NAVETTE"), 0.60, "ZTL ECCETTO NAVETTE")
check("ZTL + eccezione zona grigia (0.60) -> GO (sopra soglia rumore)", r.action == "GO")

r = decide(mkm(has_restriction=True, restriction_active=False,
               matched_restriction="ZTL", time_window=(7, 20)), 0.92, "ZTL ORARIO 7-20")
check("ZTL fuori orario → GO",         r.action == "GO")


# =============================================================================
# PIPELINE end-to-end
# =============================================================================
print("\n=== pipeline (integration) ===")
from src.pipeline import process_scenario, run_batch
from pathlib import Path

def mks(f=None, l=None, v=None, orario="09:00", giorno="Lunedì", id_=1):
    def r(t, c): return {"testo": t, "confidenza": c}
    return {
        "id_scenario": id_,
        "sensori": {
            "camera_frontale": r(*f) if f else None,
            "camera_laterale": r(*l) if l else None,
            "V2I_receiver":    r(*v) if v else None,
        },
        "orario_rilevamento": orario,
        "giorno_settimana": giorno,
    }

res = process_scenario(mks())
check("tutti null → HUMAN_CONFIRM",    res["action"] == "HUMAN_CONFIRM")

res = process_scenario(mks(f=("ZTL",0.99), l=("ZTL",0.98), v=("ZTL",0.97)))
check("ZTL tutti → STOP",              res["action"] == "STOP")

res = process_scenario(mks(f=("ZTL ECCETTO NAVETTE",0.95), l=("ZTL ECCETTO NAVETTE",0.93), v=("ZTL ECCETTO NAVETTE",0.96)))
check("ECCETTO NAVETTE tutti → GO",    res["action"] == "GO")

res = process_scenario({"id_scenario": 99})
check("campi mancanti no crash",       res["action"] == "HUMAN_CONFIRM")

res = process_scenario(mks(f=("ZTL ORARIO 7-20",0.91), l=("ZTL ORARIO 7-20",0.89), v=("ZTL ORARIO 7-20",0.95), orario="21:00"))
check("ZTL fuori orario → GO",         res["action"] == "GO")

res = process_scenario(mks(f=("ZTL",0.40), l=("ZTL",0.35)))
check("bassa conf → HUMAN_CONFIRM",    res["action"] == "HUMAN_CONFIRM")

# Schema output
for key in ("id_scenario", "action", "confidence", "reason"):
    check(f"output ha campo '{key}'",  key in res)

# Batch su file reale
results = run_batch(Path("data/input.json"))
check("batch: lista non vuota",        len(results) > 0)
check("batch: ogni item ha action",    all("action" in r for r in results))
check("batch: ogni item ha reason",    all("reason" in r and len(r["reason"]) > 0 for r in results))
check("batch: ogni item ha confidence", all("confidence" in r for r in results))
check("batch: conf in [0,1]",          all(0.0 <= r["confidence"] <= 1.0 for r in results))


# =============================================================================
# Riepilogo
# =============================================================================
print(f"\n{'='*55}")
print(f"  RISULTATO: {_passed} PASSED  |  {len(_failed)} FAILED")
if _failed:
    for f in _failed:
        print(f"    ✗ {f}")
print(f"{'='*55}\n")

if _failed:
    sys.exit(1)