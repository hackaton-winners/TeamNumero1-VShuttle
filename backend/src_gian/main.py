"""
main.py
=======
Entry point del backend navette.

Il backend produce una lista JSON:
    [
        {"id_scenario": 1, "action": "STOP",         "confidence": 0.982,  "reason": "..."},
        {"id_scenario": 2, "action": "GO",            "confidence": 0.954,  "reason": "..."},
        {"id_scenario": 3, "action": "HUMAN_CONFIRM", "confidence": 0.410,  "reason": "..."},
        ...
    ]

Il frontend effettua polling ogni 4 secondi e legge questa lista.

─────────────────────────────────────────────────────────────────────
Modalità disponibili:
  Batch (default)  →  processa input.json, stampa risultati + scrive output.json
  Live             →  rielabora input.json ogni N secondi (default 4) e chiama
                      send_to_frontend() con la lista aggiornata

Utilizzo:
  python main.py                         # batch
  python main.py --input altro.json      # batch con file custom
  python main.py --live                  # polling ogni 4s
  python main.py --live --interval 2     # polling ogni 2s
─────────────────────────────────────────────────────────────────────

Per collegare il frontend reale:
  Modifica SOLO la funzione `send_to_frontend()` qui sotto.
  Tutto il resto non va toccato.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from src.pipeline import run_batch
from src.config import INPUT_JSON_PATH

DEFAULT_INTERVAL = 4  # secondi tra un ciclo di polling e il successivo


# =============================================================================
# INTEGRAZIONE FRONTEND
# Sostituire il corpo di questa funzione con la chiamata HTTP reale.
# Esempio con httpx:
#   import httpx
#   httpx.post("http://frontend-host/api/decisions", json=results)
# =============================================================================

def send_to_frontend(results: list[dict]) -> None:
    """
    Invia la lista dei risultati al frontend.

    *** PUNTO DI INTEGRAZIONE ***
    In produzione sostituire con la chiamata HTTP/WebSocket reale.
    Attualmente stampa a console (simulazione).
    """
    ts = datetime.now().strftime("%H:%M:%S")
    colors = {
        "GO":            "\033[92m",   # verde
        "STOP":          "\033[91m",   # rosso
        "HUMAN_CONFIRM": "\033[93m",   # giallo
    }
    reset = "\033[0m"

    print(f"\n[{ts}] Lista inviata al frontend — {len(results)} scenari")
    print("─" * 78)
    for r in results:
        c = colors.get(r["action"], "")
        print(
            f"  id={r['id_scenario']:>3}  "
            f"{c}{r['action']:14}{reset}  "
            f"conf={r['confidence']:.4f}  "
            f"{r['reason'][:55]}"
        )
    print("─" * 78)


# =============================================================================
# Runners
# =============================================================================

def _run_batch(input_path: Path, output_path: Path) -> None:
    results = run_batch(input_path)
    send_to_frontend(results)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  Output salvato in: {output_path}\n")


def _run_live(input_path: Path, interval: int) -> None:
    print(f"\n  Modalità live — polling ogni {interval}s. Premi Ctrl+C per fermare.\n")
    try:
        while True:
            results = run_batch(input_path)
            send_to_frontend(results)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n  Polling interrotto.")


# =============================================================================
# CLI
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Shuttle backend: elabora scenari sensoriali → GO/STOP/HUMAN_CONFIRM"
    )
    parser.add_argument("--input",    type=Path, default=INPUT_JSON_PATH,
                        help="Path al file JSON di input")
    parser.add_argument("--output",   type=Path, default=Path("data/output.json"),
                        help="Path al file JSON di output (solo modalità batch)")
    parser.add_argument("--live",     action="store_true",
                        help="Avvia polling live invece di batch singolo")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                        help=f"Intervallo polling in secondi (default: {DEFAULT_INTERVAL})")
    args = parser.parse_args()

    if args.live:
        _run_live(args.input, args.interval)
    else:
        _run_batch(args.input, args.output)


if __name__ == "__main__":
    main()