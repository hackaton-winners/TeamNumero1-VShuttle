"""
config.py
=========
Carica tutti i parametri dal file .env nella directory del progetto.
È l'unico modulo che legge variabili d'ambiente: tutti gli altri
importano da qui, così il punto di modifica è sempre uno solo.

Non serve installare python-dotenv: il parsing è fatto a mano
per mantenere zero dipendenze esterne.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Percorso del file .env (stessa directory di config.py, ovvero root progetto)
# ---------------------------------------------------------------------------
_ENV_PATH = Path(__file__).parent / ".env"


def _load_env(path: Path) -> dict[str, str]:
    """Legge il file .env e restituisce un dict chiave→valore."""
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


_env = _load_env(_ENV_PATH)


def _get(key: str, default: str) -> str:
    """Legge la chiave dall'env file, poi dalle variabili d'ambiente di sistema."""
    return os.environ.get(key, _env.get(key, default))


def _float(key: str, default: float) -> float:
    try:
        return float(_get(key, str(default)))
    except ValueError:
        return default


# =============================================================================
# Parametri esposti al resto del progetto
# =============================================================================

# Path del file JSON di input
INPUT_JSON_PATH: Path = Path(_get("INPUT_JSON_PATH", "data/input.json"))

# Pesi IVW — server online
W_SERVER:   float = _float("W_SERVER",   0.60)
W_FRONTALE: float = _float("W_FRONTALE", 0.30)
W_LATERALE: float = _float("W_LATERALE", 0.10)

# Pesi IVW — server offline
W_FRONTALE_OFFLINE: float = _float("W_FRONTALE_OFFLINE", 0.75)
W_LATERALE_OFFLINE: float = _float("W_LATERALE_OFFLINE", 0.25)

# Soglie di confidenza
THRESHOLD_CERTAIN:   float = _float("THRESHOLD_CERTAIN",   0.75)
THRESHOLD_UNCERTAIN: float = _float("THRESHOLD_UNCERTAIN", 0.50)