"""Pontuação de um candidato, de 0 a 100, separada em título e autores para dar para explicar."""
from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz

PESO_TITULO = 0.6
SEM_AUTOR = 0.85  # sem autor dos dois lados, só o título não basta para casar sozinho


@dataclass(frozen=True)
class Pontuacao:
    total: float
    titulo: float
    autores: float | None  # None quando um dos lados não tem autor


def sim_nome(a: str, b: str) -> float:
    """Pessoa é nome e sobrenome: os dois precisam bater. "A LIMA" x "ANA LIMA" vale 90; mesmo
    sobrenome com outro primeiro nome é outra pessoa e vale pouco."""
    if a == b:
        return 100.0
    pa, pb = a.split(), b.split()
    if not pa or not pb:
        return 0.0
    sobrenome = fuzz.ratio(pa[-1], pb[-1])
    if pa[0] == pb[0]:
        primeiro = 100.0
    elif (len(pa[0]) == 1 or len(pb[0]) == 1) and pa[0][0] == pb[0][0]:
        primeiro = 90.0
    else:
        primeiro = fuzz.ratio(pa[0], pb[0])
    menor = min(sobrenome, primeiro)
    return menor if menor >= 85 else menor / 2


def sim_autores(enviados: list[str], catalogo: list[str]) -> float | None:
    """Média, entre os autores enviados, da melhor correspondência no catálogo."""
    if not enviados or not catalogo:
        return None
    return sum(max(sim_nome(e, c) for c in catalogo) for e in enviados) / len(enviados)


def pontuar(titulo: str, autores: list[str], titulo_obra: str, autores_obra: list[str]) -> Pontuacao:
    t = fuzz.token_sort_ratio(titulo, titulo_obra)
    a = sim_autores(autores, autores_obra)
    total = PESO_TITULO * t + (1 - PESO_TITULO) * a if a is not None else SEM_AUTOR * t
    return Pontuacao(round(total, 1), round(t, 1), None if a is None else round(a, 1))
