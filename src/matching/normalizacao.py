"""Normalização de títulos e nomes antes de comparar.

O que muda de um envio para outro e não muda a obra: caixa, acento, pontuação, marcação de versão
("(Ao Vivo)", "- Remix") e participação especial ("feat. Fulano") no título; e, nos nomes, a ordem
"Sobrenome, Nome".
"""
from __future__ import annotations

import re
import unicodedata

VERSAO = re.compile(r"\((?:AO VIVO|ACUSTICO|REMIX|REMASTERIZAD[AO]|VERSAO [^)]*|AO VIVO EM [^)]*)\)"
                    r"|\s-\s(?:AO VIVO|ACUSTICO|REMIX)\b.*$")
PARTICIPACAO = re.compile(r"\s(?:FEAT|FT|PART)\b\.?\s.*$")
NAO_ALFANUMERICO = re.compile(r"[^A-Z0-9 ]+")
ESPACOS = re.compile(r"\s+")
SEPARADOR_DE_LISTA = re.compile(r"[;|]")  # vírgula não separa: aparece em "Sobrenome, Nome"
VAZIAS = {"DE", "DA", "DO", "DAS", "DOS", "E", "O", "A", "OS", "AS", "UM", "UMA", "EM", "NO", "NA", "PRA",
          "PARA", "COM", "POR", "MEU", "MINHA", "TEU", "TUA"}


def sem_acentos(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def _base(texto: str | None) -> str:
    return ESPACOS.sub(" ", sem_acentos(texto or "").upper()).strip()


def titulo(texto: str | None) -> str:
    t = _base(texto)
    t = PARTICIPACAO.sub("", t)
    t = VERSAO.sub(" ", t)
    return ESPACOS.sub(" ", NAO_ALFANUMERICO.sub(" ", t)).strip()


def nome(texto: str | None) -> str:
    t = _base(texto)
    if t.count(",") == 1:  # "LIMA, ANA" -> "ANA LIMA"
        sobrenome, primeiro = (p.strip() for p in t.split(","))
        t = f"{primeiro} {sobrenome}"
    return ESPACOS.sub(" ", NAO_ALFANUMERICO.sub(" ", t)).strip()


def lista(texto: str | None) -> list[str]:
    return [n for n in (nome(p) for p in SEPARADOR_DE_LISTA.split(texto or "")) if n]


def palavras(titulo_normalizado: str) -> set[str]:
    return {p for p in titulo_normalizado.split() if p not in VAZIAS and len(p) > 1}
