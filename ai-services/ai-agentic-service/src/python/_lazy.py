"""Optional-import helpers. Heavy ML libs load only when a coarse method needs them."""

from __future__ import annotations

import importlib
import json
from typing import Any


def installed(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        return False


def require(name: str) -> Any:
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        raise RuntimeError(
            f"{name} nao instalado; use o ecossistema Python via interop, "
            "nao no domain/application Mojo"
        ) from exc


def dump(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True)


def load(payload: str) -> Any:
    if not payload:
        return {}
    return json.loads(payload)
