import multiprocessing
from ligacao_base_dados import db
from firebase_admin import firestore

def gerar_relatorio_saldos():
    """Fornecer um relatório com os utilizadores com maior saldo, 
        com menor saldo e a soma de todos os saldos
    """
    
    conta = db.collection("utilizadores").limit(1).get()
    
    if not conta:
        print("Não existem contas.\n")
        return False
    
    #Saldo total
    saldo_total = db.collection("utilizadores").sum("Saldo").get()[0][0].value
    
    # Número de contas
    quantidade_contas = db.collection("utilizadores").count().get()[0][0].value

    # Utilizadores com mais dinheiro e menos dinheiro:
    lista_user_saldo_maior, maior_saldo = saldo_ordenado(False)
    lista_user_saldo_menor, menor_saldo = saldo_ordenado(True)

    print(f"Utilizador/es {lista_user_saldo_maior} com maior saldo: {maior_saldo}")
    print(f"Utilizador/es {lista_user_saldo_menor} com menor saldo: {menor_saldo}")
    print(f"Soma de todos os saldos: {saldo_total}")
    print(f"Soma de todas as contas: {quantidade_contas}")

def gerar_relatorio_transferencias():
    """Fornecer um relatório com os utilizadores 
        que mais dinheiro receberam, mais dinheiro enviaram
        e a soma total do dinheiro transferido
    """

    # Buscar pelo menos uma transferência (não é necessário todas para validar)
    transferencias = db.collection("transferencias").limit(1).get()

    if not transferencias:
        print("Não existem transferências.\n")
        return

    # Total Transferências
    total_transferencias = db.collection("transferencias").count().get()[0][0].value

    # Total Transferido
    total_transferido = db.collection("transferencias").sum("Valor").get()[0][0].value

    orig = {}
    dest = {}

    for y in db.collection("transferencias").stream():
        y_dic = y.to_dict()
        orig[y_dic["Origem"].id] = orig.get(y_dic["Origem"].id, 0) + y_dic["Valor"]
        dest[y_dic["Destino"].id] = dest.get(y_dic["Destino"].id, 0) + y_dic["Valor"]

    # utilizadores que mais enviaram e que mais receberam
    max_enviado, mais_enviaram, _, _ = maiores_e_menores(orig)
    max_recebido, mais_receberam, _, _ = maiores_e_menores(dest)

    print("Relatório de transferências:")
    print(f"Número de transferências: {total_transferencias}")
    print(f"Valor total transferido: {total_transferido:.2f}")
    print(f"Mais enviou ({max_enviado:.2f}): {', '.join(mais_enviaram)}")
    print(f"Mais recebeu ({max_recebido:.2f}): {', '.join(mais_receberam)}\n")

def gerar_relatorios_em_paralelo():
    """Gera o relatório de saldos e o relatório de transferências ao mesmo
    tempo, cada um no seu processo, e espera que os dois terminem.
    """
    processo_1 = multiprocessing.Process(target=gerar_relatorio_saldos)
    processo_2 = multiprocessing.Process(target=gerar_relatorio_transferencias)

    processo_1.start()
    processo_2.start()
    processo_1.join()
    processo_2.join()

def consultar_transferencias(username):
    """Consultar as transferências onde o próprio utilizador está envolvido
    """

    transf_user = db.collection("utilizadores").document(username)
    utilizador_origem = firestore.FieldFilter("Origem", "==", transf_user)
    utilizador_destino = firestore.FieldFilter("Destino", "==", transf_user)
    transf_origem_destino = db.collection("transferencias").where(filter=firestore.Or([utilizador_origem, utilizador_destino]))

    transf = transf_origem_destino.limit(1).get()
    if not transf:
        print("Não existem transferências para este utilizador.\n")
        return

    # Transferências em que o utilizador é origem ou destino, da mais recente para a mais antiga
    transferencias = transf_origem_destino.order_by("Data", direction=firestore.Query.DESCENDING).stream()

    print(f"Transferências de {username}:")

    for t in transferencias:
        t_dic = t.to_dict()
        destino = t_dic["Destino"].get().id
        origem = t_dic["Origem"].get().id

        if origem == username:
            print(f"- {t_dic['Data']}  enviou  {t_dic['Valor']:.2f}€ para {destino}")
        else:
            print(f"- {t_dic['Data']}  recebeu  {t_dic['Valor']:.2f}€ de {origem}")
    print("\n")

def saldo_ordenado(order):
    """Encontra o maior ou o menor saldo e os utilizadores que o têm.

    Args:
        order (bool): True para procurar o menor saldo, False para
        procurar o maior.

    Returns:
        tuple[list[str], float]: lista dos usernames com esse saldo
        (pode haver empates) e o valor do saldo.
    """
    final_order = firestore.Query.DESCENDING

    if order:
        final_order = firestore.Query.ASCENDING

    max_min = db.collection("utilizadores").order_by("Saldo", direction=final_order).limit(1).stream()
 
    for i in max_min:
        max_min_valor = i.to_dict()["Saldo"]

    lista_utilizadores = db.collection("utilizadores").where(filter=firestore.FieldFilter("Saldo", "==", max_min_valor)).stream()

    pessoas_dinheiro = []

    for user in lista_utilizadores:
        utilizador = user.id
        pessoas_dinheiro.append(utilizador)

    return pessoas_dinheiro, max_min_valor

def maiores_e_menores(valores):
    """Encontra os usernames com o maior e com o menor valor.

    Args:
        valores (dict[str, float]): dicionário no formato {username: valor}.

    Returns:
        tuple[float, list[str], float, list[str]]: o valor máximo, os
        usernames com esse valor, o valor mínimo e os usernames com esse
        valor (pode haver empates).
    """
    maximo = max(valores.values())
    minimo = min(valores.values())
    maiores = [username for username, valor in valores.items() if valor == maximo]
    menores = [username for username, valor in valores.items() if valor == minimo]
    return maximo, maiores, minimo, menores
