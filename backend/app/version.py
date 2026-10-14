import sys
from pathlib import Path


def _read_version() -> str:
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(getattr(sys, "_MEIPASS", "")) / "VERSION")
        candidates.append(Path(sys.executable).resolve().parent / "VERSION")
    else:
        candidates.append(Path(__file__).resolve().parents[2] / "VERSION")
    for p in candidates:
        try:
            return p.read_text(encoding="utf-8").strip()
        except Exception:
            continue
    return "0.0.0"


APP_VERSION = _read_version()
