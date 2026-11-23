import pytest
from unittest.mock import MagicMock

from ModulosProjeto.pacotes import (
    modulos_criacao_e_entrada,
    modulos_funcoes_no_banco
)
from ModulosProjeto.pacotes.modulos_excecoes import (
    UtilizadorJaExisteError,
    UtilizadorInexistenteError,
    SaldoInsuficienteError,
)
from ModulosProjeto.pacotes.modulos_criacao_e_entrada import (
    criar_utilizador,
)
from ModulosProjeto.pacotes.modulos_funcoes_no_banco import (
    transferir
)

def test_utilizador_duplicado(monkeypatch):
    """Verifica que criar um utilizador com um username já existente
    levanta UtilizadorJaExisteError.

    Args:
        monkeypatch (pytest.MonkeyPatch): usado para substituir a base de
        dados e simular o input do utilizador.
    """
    db_falsa = MagicMock()
    documento = db_falsa.collection.return_value.document
    documento.return_value.get.return_value.to_dict.return_value = {"Username": "ana"}

    monkeypatch.setattr(modulos_criacao_e_entrada, "db", db_falsa)
    monkeypatch.setattr("builtins.input", lambda _: "ana")

    with pytest.raises(UtilizadorJaExisteError):
        criar_utilizador()

    documento.assert_called_once_with("ana") #Expected
    documento.return_value.set.assert_not_called() #Actual

def test_utilizador_inexistente_transferencia(monkeypatch):
    """Verifica que transferir para um utilizador que não existe
    levanta UtilizadorInexistenteError.

    Args:
        monkeypatch (pytest.MonkeyPatch): usado para substituir a base de
        dados e simular o input do utilizador.
    """
    db_falsa = MagicMock()

    ana = MagicMock()
    ana.get.return_value.exists = True
    
    zeca = MagicMock()
    zeca.get.return_value.exists = False
    
    contas = {"ana": ana, "zeca": zeca}
    db_falsa.collection.return_value.document.side_effect = lambda username: contas[username]

    monkeypatch.setattr(modulos_funcoes_no_banco, "db", db_falsa)

    respostas = iter(["zeca", "50"])  # [destino, valor]
    monkeypatch.setattr("builtins.input", lambda _: next(respostas))

    with pytest.raises(UtilizadorInexistenteError):
        transferir("ana", None, None)
    
    transacao = db_falsa.transaction.return_value
    transacao.update.assert_not_called() #Expected
    transacao.create.assert_not_called() #Actual
 
def test_transferencia_sucesso(monkeypatch, capsys):
    """Verifica que uma transferência válida termina com a mensagem de sucesso.

    Args:
        monkeypatch (pytest.MonkeyPatch): usado para substituir a base de
        dados e simular o input do utilizador.
        capsys (pytest.CaptureFixture): usado para ler o que foi impresso.
    """

    db_falsa = MagicMock()

    ana = MagicMock()
    ana.get.return_value.exists = True
    ana.get.return_value.get.return_value = 100
    
    zeca = MagicMock()
    zeca.get.return_value.exists = True
    
    contas = {"ana": ana, "zeca": zeca}
    db_falsa.collection.return_value.document.side_effect = lambda username=None: contas.get(username)

    monkeypatch.setattr(modulos_funcoes_no_banco, "db", db_falsa)

    respostas = iter(["zeca", "50"])  # [destino, valor]
    monkeypatch.setattr("builtins.input", lambda _: next(respostas))

    assert transferir("ana", None, None) is True

    saida = capsys.readouterr().out
    assert "Transferência de 50.00 realizada com sucesso" in saida
    
    transacao = db_falsa.transaction.return_value
    assert transacao.update.call_count == 2 #Expected
    transacao.create.assert_called_once() #Actual

def test_saldo_insuficiente(monkeypatch):
    """Verifica que transferir mais do que o saldo disponível
    levanta SaldoInsuficienteError.

    Simula duas contas existentes ("ana" com saldo 2 e "zeca") e tenta
    transferir 50 da ana para o zeca.

    Args:
        monkeypatch (pytest.MonkeyPatch): usado para substituir a base de
        dados por uma falsa e simular o input do utilizador.
    """
    db_falsa = MagicMock()
    
    ana = MagicMock()
    ana.get.return_value.exists = True
    ana.get.return_value.get.return_value = 2
    
    zeca = MagicMock()
    zeca.get.return_value.exists = True
        
    conta = {"ana": ana, "zeca": zeca}
    db_falsa.collection.return_value.document.side_effect = lambda username=None: conta.get(username)

    monkeypatch.setattr(modulos_funcoes_no_banco, "db", db_falsa)

    respostas = iter(["zeca", "50"]) #[destino, valor]
    monkeypatch.setattr("builtins.input", lambda _: next(respostas))

    with pytest.raises(SaldoInsuficienteError):
        transferir("ana", None, None)
    
    transacao = db_falsa.transaction.return_value
    transacao.update.assert_not_called()
    transacao.create.assert_not_called()

if __name__ == "__main__":
    pytest.main()
