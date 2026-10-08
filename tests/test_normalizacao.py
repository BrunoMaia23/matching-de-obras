import pytest

from matching import normalizacao as n


@pytest.mark.parametrize("enviado, esperado", [
    ("Saudade do Sertão", "SAUDADE DO SERTAO"),
    ("SAUDADE DO SERTAO (Ao Vivo)", "SAUDADE DO SERTAO"),
    ("Saudade do Sertão (Ao Vivo em Recife)", "SAUDADE DO SERTAO"),
    ("Saudade do Sertão - Remix", "SAUDADE DO SERTAO"),
    ("Saudade do Sertão feat. Ana Lima", "SAUDADE DO SERTAO"),
    ("Saudade do Sertão (Acústico) ft. Ana", "SAUDADE DO SERTAO"),
    ("Saudade,  do   Sertão!", "SAUDADE DO SERTAO"),
    ("Partida", "PARTIDA"),                   # "PART" só conta como participação se for a palavra inteira
])
def test_titulo(enviado, esperado):
    assert n.titulo(enviado) == esperado


@pytest.mark.parametrize("enviado, esperado", [
    ("Ana Lima", "ANA LIMA"),
    ("Lima, Ana", "ANA LIMA"),
    ("Nícolas Valença", "NICOLAS VALENCA"),
    ("A. Lima", "A LIMA"),
])
def test_nome(enviado, esperado):
    assert n.nome(enviado) == esperado


def test_lista_separa_por_ponto_e_virgula_e_barra_mas_nao_por_virgula():
    assert n.lista("Lima, Ana; Duarte, Pedro | Olga Macedo") == ["ANA LIMA", "PEDRO DUARTE", "OLGA MACEDO"]


def test_palavras_ignoram_ligacoes():
    assert n.palavras("SAUDADE DO SERTAO E A LUA") == {"SAUDADE", "SERTAO", "LUA"}
