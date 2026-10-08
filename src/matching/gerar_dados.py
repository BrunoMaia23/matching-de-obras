"""Catálogo fictício, planilhas do parceiro (nos dois formatos) e o gabarito do que é o quê.

As linhas que existem no catálogo chegam com as variações de sempre: sem acento, tudo em maiúscula,
erro de digitação, "(Ao Vivo)", "feat.", nome invertido, primeiro nome abreviado, autor faltando. As
obras novas usam o mesmo vocabulário de títulos, de propósito: título igual com autor diferente não
pode virar casamento automático.
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

from openpyxl import Workbook

from .normalizacao import sem_acentos

PALAVRAS = ["Saudade", "Aurora", "Sertão", "Luar", "Estrada", "Maré", "Coração", "Cidade", "Varanda",
            "Ventania", "Horizonte", "Caminho", "Janela", "Riacho", "Fogueira", "Serena", "Lembrança",
            "Promessa", "Viola", "Batuque", "Ciranda", "Quintal", "Retrato", "Aquarela", "Travessia",
            "Morena", "Farol", "Primavera", "Andorinha", "Cantiga", "Alvorada", "Desejo", "Destino",
            "Saveiro", "Moenda", "Jangada", "Bandeira", "Sereno", "Ladeira", "Mirante"]
LIGACOES = ["de", "do", "da", "no", "na", "pra", "e"]
NOMES = ["Ana", "Bruna", "Carla", "Diego", "Elisa", "Fábio", "Gabriela", "Heitor", "Isadora", "Jonas",
         "Karina", "Leandro", "Marina", "Nícolas", "Olga", "Pedro", "Priscila", "Renata", "Sérgio",
         "Tânia", "Vítor", "Wagner", "Yara", "Zélia"]
SOBRENOMES = ["Almeida", "Barbosa", "Cardoso", "Duarte", "Esteves", "Fonseca", "Guimarães", "Holanda",
              "Jardim", "Lacerda", "Macedo", "Nogueira", "Pacheco", "Queiroz", "Rangel", "Siqueira",
              "Tavares", "Valença", "Xavier", "Moreira"]
EDITORAS = ["Editora Aurora", "Edições Horizonte", "Selo Maré", "Editora Varanda", "Música do Farol",
            "Edições Mirante", "Selo Quintal", "Editora Alvorada"]
VERSOES = [" (Ao Vivo)", " (Acústico)", " - Remix", " (Ao Vivo em Recife)"]


def _titulo(rng: random.Random) -> str:
    n = rng.choice([1, 2, 2, 3, 3, 4])
    palavras = rng.sample(PALAVRAS, n)
    if n >= 2 and rng.random() < 0.6:
        palavras.insert(1, rng.choice(LIGACOES))
    return " ".join(palavras)


def _erro_de_digitacao(rng: random.Random, texto: str) -> str:
    palavras = texto.split()
    i = max(range(len(palavras)), key=lambda k: len(palavras[k]))
    p = palavras[i]
    if len(p) > 4:
        j = rng.randrange(1, len(p) - 1)
        palavras[i] = p[:j] + p[j + 1:] if rng.random() < 0.5 else p[:j] + p[j + 1] + p[j] + p[j + 2:]
    return " ".join(palavras)


def _variar(rng: random.Random, obra: dict, autores: list[str]) -> tuple[str, list[str]]:
    titulo, envio = obra["titulo"], list(autores)
    for variacao in rng.sample(["acento", "caixa", "digitacao", "versao", "feat", "invertido",
                                "abreviado", "sem_autor"], rng.choice([0, 1, 1, 2, 2, 3])):
        if variacao == "acento":
            titulo, envio = sem_acentos(titulo), [sem_acentos(a) for a in envio]
        elif variacao == "caixa":
            titulo = titulo.upper()
        elif variacao == "digitacao":
            titulo = _erro_de_digitacao(rng, titulo)
        elif variacao == "versao":
            titulo += rng.choice(VERSOES)
        elif variacao == "feat":
            titulo += f" feat. {rng.choice(NOMES)} {rng.choice(SOBRENOMES)}"
        elif variacao == "invertido" and envio:
            primeiro, *resto = envio[0].split()
            envio[0] = f"{' '.join(resto)}, {primeiro}"
        elif variacao == "abreviado" and envio and "," not in envio[0]:
            primeiro, *resto = envio[0].split()
            envio[0] = f"{primeiro[0]}. {' '.join(resto)}"
        elif variacao == "sem_autor":
            envio = envio[:-1]
    return titulo, envio


def gerar(destino: Path | str, semente: int = 5, obras: int = 3000) -> dict[str, int]:
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    rng = random.Random(semente)
    autores = sorted({f"{n} {s}" for n in NOMES for s in SOBRENOMES})
    rng.shuffle(autores)
    pool, de_fora = autores[:400], autores[400:]  # autores que nunca aparecem no catálogo

    catalogo = []
    for i in range(1, obras + 1):
        catalogo.append({"codigo": f"OB{i:06d}", "titulo": _titulo(rng),
                         "autores": rng.sample(pool, rng.choice([1, 1, 2, 2, 3])), "editora": rng.choice(EDITORAS)})
    with open(destino / "catalogo.csv", "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=["codigo", "titulo", "autores", "editora"])
        escritor.writeheader()
        escritor.writerows({**o, "autores": ";".join(o["autores"])} for o in catalogo)

    gabarito = []
    lotes = {"lote_1.xlsx": (190, 30, "obra"), "lote_2.xlsx": (150, 30, "participante")}
    sorteadas = iter(rng.sample(catalogo, sum(e for e, _, _ in lotes.values())))
    for arquivo, (existentes, novas, formato) in lotes.items():
        linhas = []
        for _ in range(existentes):
            obra = next(sorteadas)
            titulo, envio = _variar(rng, obra, obra["autores"])
            linhas.append((titulo, envio, obra["codigo"]))
        for _ in range(novas):
            linhas.append((_titulo(rng), rng.sample(de_fora, rng.choice([1, 2])), ""))
        rng.shuffle(linhas)
        registros = []
        for n, (titulo, envio, codigo) in enumerate(linhas, start=1):
            id_linha = f"{arquivo[:6]}-{n:04d}"
            registros.append({"ID_LINHA": id_linha, "TITULO": titulo, "AUTORES": envio,
                              "INTERPRETES": [f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)}"],
                              "EDITORAS": [rng.choice(EDITORAS)]})
            gabarito.append({"id_linha": id_linha, "codigo": codigo})
        _planilha(destino / arquivo, registros, formato)
    with open(destino / "gabarito.csv", "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=["id_linha", "codigo"])
        escritor.writeheader()
        escritor.writerows(gabarito)
    return {"obras_no_catalogo": len(catalogo), "linhas_do_parceiro": len(gabarito),
            "existentes": sum(1 for g in gabarito if g["codigo"]), "novas": sum(1 for g in gabarito if not g["codigo"])}


def _planilha(caminho: Path, registros: list[dict], formato: str) -> None:
    livro = Workbook()
    aba = livro.active
    if formato == "obra":
        aba.append(["ID_LINHA", "TITULO", "AUTORES", "INTERPRETES", "EDITORAS"])
        for r in registros:
            aba.append([r["ID_LINHA"], r["TITULO"], "; ".join(r["AUTORES"]), "; ".join(r["INTERPRETES"]),
                        "; ".join(r["EDITORAS"])])
    else:
        aba.append(["ID_LINHA", "TITULO", "PARTICIPANTE", "FUNCAO"])
        for r in registros:
            for funcao, campo in (("AUTOR", "AUTORES"), ("INTERPRETE", "INTERPRETES"), ("EDITORA", "EDITORAS")):
                for nome in r[campo]:
                    aba.append([r["ID_LINHA"], r["TITULO"], nome, funcao])
    livro.save(caminho)
