import datetime
from ligacao_base_dados import db
from firebase_admin import firestore

from ModulosProjeto.pacotes.modulos_excecoes import (
    UtilizadorInexistenteError, 
    ProprioUtilizadorError, 
    SaldoInsuficienteError
)

def depositar(username):
    """Solicita um valor ao utilizador e atualiza esses dados
    
    Args:
        username (str): nome do username do utilizador logado
    
    Return:
        false | se falhar
    """

    conta = db.collection("utilizadores").document(username)
    get_conta = conta.get()
    if not get_conta.exists:
        print("Conta não existe\n")
        return False
    
    valor_depositar = float(input("Qual o valor que quer depositar: "))
    
    if valor_depositar <= 0:
        print("O valor deve ser maior que zero.\n")
        return False
    else:
        conta.update({"Saldo": firestore.Increment(valor_depositar)})
        print(f"Depositado {valor_depositar} na conta de {username}.\n")


def consultar_saldo(username):
    """Consulta o saldo da conta do utilizador.

    Args:
        username (str): username do utilizador que está logado.

    Returns:
        str | None: mensagem com o saldo formatado com 2 casas decimais,
        ou None se a conta não existir.
    """
    conta = db.collection("utilizadores").document(username).get()
    conteudo = conta.to_dict()
    print(username)
    if conta.exists:
        return f"O valor do saldo é: {conteudo["Saldo"]:.2f}\n"


def consultar_retorno(numero_meses, taxa_juro, username):
    """Consultar retorno com Taxa de Juro Composto e com recursividade
    Se os dois valores forem None, a função pede-os com input()

    Args:
        numero_meses (int): número de meses, entre 1 e 12.
        taxa_juro (float): taxa de juro mensal em percentagem, entre 0 e 100.
        username (string): nome do username que está loggado.

    Returns:
        float | None: saldo da conta com juro composto aplicado, ou None se a
        taxa ou o número de meses forem inválidos.
        false | quando a conta não existe.
    """
    if numero_meses == None and taxa_juro == None:
        taxa_juro = float(input("Insira um valor de Juro entre 0 e 100: "))
        numero_meses = int(input("Insira o numero de meses de 1 a 12: "))
    
    conta = db.collection("utilizadores").document(username).get()
    conteudo = conta.to_dict()
    if not conta.exists:
        print("Conta não existe\n")
        return False
    
    if not (0 <= taxa_juro <= 100 and 1 <= numero_meses <= 12):
        print("Taxa de juro inserido inválido ou Numero de meses inválido")
        return

    if numero_meses == 1:
        return conteudo["Saldo"] * (1 + (taxa_juro / 100)** numero_meses)
    else:
        return consultar_retorno(numero_meses - 1, taxa_juro, username) * (1 + taxa_juro / 100)

@firestore.transactional
def transferir_transacao(transaction, username_origem, username_destino, valor):
    """Executa a transferência dentro de uma transação do Firestore.

    Retira o valor da conta de origem, adiciona-o à conta de destino e
    guarda o registo na coleção "transferencias". Como é uma transação,
    ou todas as alterações são feitas, ou nenhuma é.

    Args:
        transaction (firestore.Transaction): transação onde as operações
        são feitas.
        username_origem (firestore.DocumentReference): documento da conta
        que envia o dinheiro.
        username_destino (firestore.DocumentReference): documento da conta
        que recebe o dinheiro.
        valor (float): quantidade a transferir.

    Raises:
        UtilizadorInexistenteError: se a conta de origem ou de destino
        não existir.
        SaldoInsuficienteError: se o saldo da conta de origem for inferior
        ao valor.
    """

    origem = username_origem.get(transaction=transaction)
    destino = username_destino.get(transaction=transaction)

    if not origem.exists or not destino.exists:
        raise UtilizadorInexistenteError("Utilizador não existe")

    if origem.get("Saldo") < valor:
        raise SaldoInsuficienteError("Saldo insuficiente")

    transaction.update(username_origem, {"Saldo": firestore.Increment(-valor)})
    transaction.update(username_destino, {"Saldo": firestore.Increment(valor)})
    transaction.create(db.collection("transferencias").document(), {
        "Data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Valor": valor,
        "Origem": username_origem,
        "Destino": username_destino,
    })


def transferir(username_origem, username_destino, valor):
    """Pede o destino e o valor ao utilizador e transfere o dinheiro.

    Os argumentos username_destino e valor são ignorados, porque a função
    pede-os com input().

    Args:
        username_origem (str): username do utilizador que está logado.
        username_destino (str | None): ignorado.
        valor (float | None): ignorado.

    Returns:
        bool: True se a transferência foi concluída, ou False se o valor
        for menor ou igual a 0.

    Raises:
        ProprioUtilizadorError: se o utilizador tentar transferir para
        a própria conta.
        UtilizadorInexistenteError: se a conta de origem ou de destino
        não existir.
        SaldoInsuficienteError: se o saldo for inferior ao valor.
    """
    username_destino = input("Qual é a conta a quem quer transferir o dinheiro: ")
    valor = float(input("Qual é a quantidade que quer transferir?"))
    
    if valor <= 0:
        print("O valor deve ser maior que 0.\n")
        return False
    if username_origem == username_destino:
        raise ProprioUtilizadorError("Não é possível transferir para si próprio.\n")

    transaction = db.transaction()

    # Em caso de erro na função transferir_transacao, testa novamente
    # Se for um erro das exceptions já criadas, ele salta logo fora
    # Faz isso 5 vezes por default e dá Aborted
    transferir_transacao(
        transaction,
        db.collection("utilizadores").document(username_origem),
        db.collection("utilizadores").document(username_destino),
        valor
    )
    # Só acontece se der commit final
    print(f"Transferência de {valor:.2f} realizada com sucesso.\n")
    return True
