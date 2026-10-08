"""Casamento de obras de um parceiro com o catálogo: recebe as planilhas, casa e gera a revisão."""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

from . import avaliacao, casamento, entrada, gerar_dados, saida
from .decisao import CASADA, DUVIDA, PENDENTE

MARCADOR = ".matching-demo"


def receber(base: Path, planilhas: list[Path]) -> None:
    staging = entrada.Staging(base / "staging.sqlite")
    try:
        for p in planilhas:
            linhas = entrada.ler_planilha(p)
            novas, vistas = staging.receber(p, linhas)
            print(f"[entrada]    {p.name}: {novas} linhas novas, {vistas} já recebidas")
    finally:
        staging.fechar()


def casar(base: Path, catalogo_csv: Path) -> list[casamento.Resultado]:
    inicio = time.perf_counter()
    catalogo = casamento.ler_catalogo(catalogo_csv)
    staging = entrada.Staging(base / "staging.sqlite")
    try:
        resultados = [casamento.casar(l, catalogo) for l in staging.todas()]
    finally:
        staging.fechar()
    c = Counter(r.decisao.status for r in resultados)
    print(f"[casamento]  {len(resultados)} linhas contra {len(catalogo.obras)} obras em "
          f"{time.perf_counter() - inicio:.1f}s: {c[CASADA]} casadas, {c[DUVIDA]} em dúvida, {c[PENDENTE]} pendentes")
    saida.gravar(base / "resultado.xlsx", resultados, catalogo)
    print("[saída]      resultado.xlsx com as abas Casadas, Duvidas, Pendentes e Resumo")
    return resultados


def demo(base: Path) -> int:
    if base.exists():
        if not (base / MARCADOR).exists():
            print(f"A pasta {base} já existe e não foi criada pela demo; escolha outra com --base.")
            return 2
        shutil.rmtree(base)
    base.mkdir(parents=True)
    (base / MARCADOR).write_text("pasta da demo do matching\n", encoding="utf-8")
    d = gerar_dados.gerar(base)
    print(f"[dados]      catálogo com {d['obras_no_catalogo']} obras; {d['linhas_do_parceiro']} linhas do parceiro "
          f"em 2 planilhas ({d['existentes']} existem no catálogo, {d['novas']} são novas)")
    receber(base, [base / "lote_1.xlsx", base / "lote_2.xlsx"])
    receber(base, [base / "lote_1.xlsx"])  # reenvio
    resultados = casar(base, base / "catalogo.csv")
    a = avaliacao.avaliar(resultados, base / "gabarito.csv")
    print(f"[gabarito]   casadas certas: {a.casadas_certas} de {a.casadas} ({a.precisao:.1%}); "
          f"das {a.existentes} que existem no catálogo, {a.casadas_certas} casaram sozinhas, "
          f"{a.existentes_em_duvida} foram para revisão e {a.existentes_pendentes} ficaram pendentes")
    print(f"[gabarito]   das {a.novas} obras novas, {a.novas_casadas} casaram por engano")
    return 0 if a.novas_casadas == 0 and a.precisao >= 0.98 else 1


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="matching", description=__doc__)
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("demo", help="gera dados fictícios, casa e confere contra o gabarito")
    p.add_argument("--base", type=Path, default=Path("demo"))
    p = sub.add_parser("receber", help="grava na staging as linhas novas das planilhas")
    p.add_argument("planilhas", type=Path, nargs="+")
    p.add_argument("--base", type=Path, default=Path("."))
    p = sub.add_parser("casar", help="casa tudo o que está na staging e gera resultado.xlsx")
    p.add_argument("--catalogo", type=Path, required=True)
    p.add_argument("--base", type=Path, default=Path("."))
    a = parser.parse_args(argv)
    if a.comando == "demo":
        return demo(a.base)
    if a.comando == "receber":
        receber(a.base, a.planilhas)
    elif a.comando == "casar":
        casar(a.base, a.catalogo)
    return 0
