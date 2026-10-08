from matching.candidatos import Indice
from matching.decisao import CASADA, DUVIDA, PENDENTE, decidir
from matching.pontuacao import Pontuacao, pontuar, sim_autores, sim_nome


def test_nome_igual_abreviado_e_outra_pessoa():
    assert sim_nome("ANA LIMA", "ANA LIMA") == 100
    assert sim_nome("A LIMA", "ANA LIMA") == 90
    assert sim_nome("ZELIA QUEIROZ", "WAGNER QUEIROZ") < 30   # mesmo sobrenome, outra pessoa
    assert sim_nome("WAGNER SIQUEIRA", "WAGNER QUEIROZ") < 50
    assert sim_nome("ISADORA MOREIRA", "ISADORA MOREIRAA") >= 90  # erro de digitação no sobrenome


def test_autores_sem_dado_de_um_lado():
    assert sim_autores([], ["ANA LIMA"]) is None
    assert sim_autores(["ANA LIMA", "PEDRO DUARTE"], ["PEDRO DUARTE", "ANA LIMA"]) == 100


def test_pontuacao_separa_titulo_e_autores():
    p = pontuar("SAUDADE DO SERTAO", ["ANA LIMA"], "SAUDADE DO SERTAO", ["ANA LIMA"])
    assert p == Pontuacao(100.0, 100.0, 100.0)
    sem_autor = pontuar("SAUDADE DO SERTAO", [], "SAUDADE DO SERTAO", ["ANA LIMA"])
    assert sem_autor.autores is None and sem_autor.total == 85.0     # nunca casa sozinho


def _p(total):
    return Pontuacao(total, total, total)


def test_decisao():
    assert decidir([]).status == PENDENTE
    assert decidir([("A", _p(65))]).status == PENDENTE
    assert decidir([("A", _p(95)), ("B", _p(80))]).status == CASADA
    assert decidir([("A", _p(95)), ("B", _p(91))]).status == DUVIDA      # dois candidatos colados
    assert decidir([("A", _p(85))]).status == DUVIDA
    d = decidir([("B", _p(75)), ("A", _p(95)), ("C", _p(70)), ("D", _p(60))])
    assert d.codigo == "A" and [c for c, _ in d.ranking] == ["A", "B", "C"]


INDICE = Indice({"OB1": "RIACHO DA JANGADA", "OB2": "RIACHO BANDEIRA", "OB3": "RIACHO NA MOENDA",
                 "OB4": "SAUDADE", "OB5": "SAUDADE DE MARE", "OB6": "CIRANDA"})


def test_titulo_identico_vem_antes_de_titulo_que_so_contem_a_palavra():
    assert INDICE.candidatos("SAUDADE")[0] == "OB4"


def test_erro_de_digitacao_numa_palavra_nao_tira_a_obra_da_lista():
    assert INDICE.corrigir("JANGAAD") == "JANGADA"
    assert INDICE.candidatos("RIACHO DA JANGAAD")[0] == "OB1"


def test_sem_palavra_em_comum_procura_pela_inicial():
    assert INDICE.candidatos("CIRNADA")[0] == "OB6"
