"""Catálogo em memória e o casamento de cada linha recebida."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from . import normalizacao
from .candidatos import Indice
from .decisao import Decisao, decidir
from .entrada import Linha
from .pontuacao import pontuar


class Catalogo:
    def __init__(self, obras: list[dict]):
        """`obras`: dicionários com codigo, titulo e autores (lista)."""
        self.obras = {o["codigo"]: o for o in obras}
        self.titulos = {c: normalizacao.titulo(o["titulo"]) for c, o in self.obras.items()}
        self.autores = {c: [normalizacao.nome(a) for a in o["autores"]] for c, o in self.obras.items()}
        self.indice = Indice(self.titulos)


@dataclass(frozen=True)
class Resultado:
    linha: Linha
    titulo_normalizado: str
    decisao: Decisao


def ler_catalogo(caminho: Path | str) -> Catalogo:
    with open(caminho, encoding="utf-8", newline="") as f:
        return Catalogo([{"codigo": r["codigo"], "titulo": r["titulo"], "editora": r["editora"],
                          "autores": [a for a in r["autores"].split(";") if a]} for r in csv.DictReader(f)])


def casar(linha: Linha, catalogo: Catalogo) -> Resultado:
    titulo = normalizacao.titulo(linha.titulo)
    autores = [normalizacao.nome(a) for a in linha.autores]
    pontuados = [(codigo, pontuar(titulo, autores, catalogo.titulos[codigo], catalogo.autores[codigo]))
                 for codigo in catalogo.indice.candidatos(titulo)]
    return Resultado(linha, titulo, decidir(pontuados))
