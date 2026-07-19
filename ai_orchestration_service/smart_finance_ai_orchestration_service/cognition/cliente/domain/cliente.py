# domain/cliente.py
from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True, frozen=True)
class Cliente:
    id: int
    nome: str
    documento: str
    criado_em: datetime | None = None