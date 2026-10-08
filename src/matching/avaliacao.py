"""Resultado contra o gabarito: quanto do automático estava certo e quanto ficou para revisão."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .casamento import Resultado
from .decisao import CASADA, DUVIDA, PENDENTE


@dataclass(frozen=True)
class Avaliacao:
    casadas: int
    casadas_certas: int
    existentes: int        # linhas que têm obra no catálogo
    existentes_em_duvida: int
    existentes_pendentes: int
    novas: int             # linhas sem obra no catálogo
    novas_casadas: int     # casamento automático errado com obra que não é a mesma

    @property
    def precisao(self) -> float:
        return self.casadas_certas / self.casadas if self.casadas else 1.0

    @property
    def cobertura(self) -> float:
        return self.casadas_certas / self.existentes if self.existentes else 1.0


def avaliar(resultados: list[Resultado], gabarito_csv: Path | str) -> Avaliacao:
    with open(gabarito_csv, encoding="utf-8", newline="") as f:
        gabarito = {g["id_linha"]: g["codigo"] for g in csv.DictReader(f)}
    existentes = [r for r in resultados if gabarito[r.linha.id_linha]]
    novas = [r for r in resultados if not gabarito[r.linha.id_linha]]
    casadas = [r for r in resultados if r.decisao.status == CASADA]
    return Avaliacao(
        casadas=len(casadas),
        casadas_certas=sum(1 for r in casadas if r.decisao.codigo == gabarito[r.linha.id_linha]),
        existentes=len(existentes),
        existentes_em_duvida=sum(1 for r in existentes if r.decisao.status == DUVIDA),
        existentes_pendentes=sum(1 for r in existentes if r.decisao.status == PENDENTE),
        novas=len(novas),
        novas_casadas=sum(1 for r in novas if r.decisao.status == CASADA),
    )
