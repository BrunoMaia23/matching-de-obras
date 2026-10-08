"""Índice do catálogo para achar candidatos sem comparar cada linha com todas as obras.

Índice invertido por palavra do título. A nota de cada candidato é a sobreposição ponderada pela
raridade da palavra (idf) dividida pela união, então o título idêntico vem antes do título que só
contém a mesma palavra. Título que não divide nenhuma palavra com o catálogo, como uma palavra só com
erro de digitação, ainda tem uma segunda chance: os títulos com a mesma inicial, por similaridade.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict

from rapidfuzz import fuzz, process

from .normalizacao import palavras

CORRECAO_MINIMA = 80  # palavra fora do vocabulário vira a mais parecida, se for parecida o bastante


class Indice:
    def __init__(self, titulos: dict[str, str]):
        """`titulos`: código da obra -> título já normalizado."""
        self.titulos = titulos
        self.por_palavra: dict[str, set[str]] = defaultdict(set)
        self.por_inicial: dict[str, list[str]] = defaultdict(list)
        for codigo, t in sorted(titulos.items()):
            for p in palavras(t):
                self.por_palavra[p].add(codigo)
            self.por_inicial[t[:1]].append(codigo)
        total = len(titulos)
        self.idf = {p: math.log(total / len(codigos)) + 1 for p, codigos in self.por_palavra.items()}
        self.peso = {c: sum(self.idf[p] for p in palavras(t)) for c, t in titulos.items()}
        self.vocabulario = sorted(self.por_palavra)

    def corrigir(self, palavra: str) -> str:
        """Erro de digitação numa palavra ("JANGAAD") não pode tirar a obra certa da lista."""
        if palavra in self.por_palavra:
            return palavra
        achada = process.extractOne(palavra, self.vocabulario, scorer=fuzz.ratio, score_cutoff=CORRECAO_MINIMA)
        return achada[0] if achada else palavra

    def candidatos(self, titulo_normalizado: str, limite: int = 30) -> list[str]:
        consulta = {self.corrigir(p) for p in palavras(titulo_normalizado)}
        peso_consulta = sum(self.idf.get(p, 1.0) for p in consulta)
        comum: Counter = Counter()
        for p in consulta:
            for codigo in self.por_palavra.get(p, ()):
                comum[codigo] += self.idf[p]
        if comum:
            nota = {c: v / (peso_consulta + self.peso[c] - v) for c, v in comum.items()}
        else:
            nota = {c: fuzz.ratio(titulo_normalizado, self.titulos[c])
                    for c in self.por_inicial.get(titulo_normalizado[:1], ())}
        return [c for c, _ in sorted(nota.items(), key=lambda kv: (-kv[1], kv[0]))[:limite]]
