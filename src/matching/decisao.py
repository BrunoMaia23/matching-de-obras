"""Decisão por linha: casada, em dúvida (vai para revisão de alguém) ou pendente."""
from __future__ import annotations

from dataclasses import dataclass, field

from .pontuacao import Pontuacao

CASADA, DUVIDA, PENDENTE = "CASADA", "DUVIDA", "PENDENTE"
LIMIAR_CASADA = 88.0
LIMIAR_DUVIDA = 70.0
MARGEM = 6.0  # o primeiro precisa ganhar do segundo por pelo menos isso


@dataclass(frozen=True)
class Decisao:
    status: str
    codigo: str | None = None
    ranking: list[tuple[str, Pontuacao]] = field(default_factory=list)  # até 3 candidatos


def decidir(pontuados: list[tuple[str, Pontuacao]]) -> Decisao:
    ranking = sorted(pontuados, key=lambda cp: (-cp[1].total, cp[0]))[:3]
    if not ranking or ranking[0][1].total < LIMIAR_DUVIDA:
        return Decisao(PENDENTE, ranking=ranking)
    primeiro = ranking[0][1].total
    segundo = ranking[1][1].total if len(ranking) > 1 else 0.0
    if primeiro >= LIMIAR_CASADA and primeiro - segundo >= MARGEM:
        return Decisao(CASADA, ranking[0][0], ranking)
    return Decisao(DUVIDA, ranking=ranking)
