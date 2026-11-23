from ModulosProjeto.pacotes.modulos_excecoes import (
    CampoVazio,
    UtilizadorInexistenteError,
    UtilizadorJaExisteError
)
from ligacao_base_dados import db

def criar_utilizador():
    """Permite criar o username e password do utilizador e guarda a 
        informação no firebase

    Raises:
        modulos_excecoes.UtilizadorJaExisteError: se o username já existir 
        no firebase
        modulos_excecoes.CampoVazio: se o campo estiver vazio
    """
    user_validacao = False
    pass_validacao = False
    

    while user_validacao is False:
        username = input("Insira um username: ")
        
        if not username:
            raise CampoVazio("Campo está vazio")
        
        conta = db.collection("utilizadores").document(username).get()
        conteudo = conta.to_dict()

        if conteudo is None:
            print("Username criada com sucesso\n")

            while pass_validacao is False:
                password = input("Insira um password: ")
                # Tamanho compreendido entre 6 - 10; Necessita de, pelo menos, 1 número e 1 caracter
                if (
                    len(password) >= 6
                    and len(password) <= 10
                    and any(char.isdigit() for char in password)
                    and any(char.isalpha() for char in password)
                ):
                    print("Password criada com sucesso\n")

                    db.collection("utilizadores").document(username).set({
                        "Username": username,
                        "Password": password,
                        "Saldo": 0
                    })
                    print("Conta criada com sucesso!")
                    pass_validacao = True
                else:
                    print("Password não apresenta todos os critérios solicitados!\n")
            user_validacao = True
        else:
            raise UtilizadorJaExisteError("Username já existe!")

def entrar():
    """Realiza a validação dos dados, tanto do username como do password, para o utilizador
    poder aceder à sua conta no banco.
    
    Raise:
        modulos_excecoes.UtilizadorInexistenteError: se o username não existir
        modulos_excecoes.CampoVazio: se o campo estiver vazio

    Returns:
        devolve o username
    """
    
    username = input("Insira o username: ")
    password = input("Insira o password: ")
    
    if not username:
        raise CampoVazio("Campo está vazio")
        
    conta = db.collection("utilizadores").document(username).get()
    conteudo = conta.to_dict()

    if conteudo is None or conteudo["Password"] != password:
        raise UtilizadorInexistenteError("Utilizador não existe!")
        
    else:
        print("Dados inseridos corretamente.\n")
        return username

