import pyfiglet
from ModulosProjeto.pacotes.modulos_relatorios import (
    gerar_relatorios_em_paralelo,
    consultar_transferencias
)

from ModulosProjeto.pacotes.modulos_excecoes import (
    UtilizadorJaExisteError,
    UtilizadorInexistenteError,
    SaldoInsuficienteError,
    ProprioUtilizadorError,
    CampoVazio
)

from ModulosProjeto.pacotes.modulos_criacao_e_entrada import (
    criar_utilizador,
    entrar
)

from ModulosProjeto.pacotes.modulos_funcoes_no_banco import (
    depositar,
    consultar_saldo,
    consultar_retorno,
    transferir
)

# Apresentação do Menu
def menu():
    """Mostra o menu principal e, depois do login, o menu da conta.

    Repete até o utilizador escolher a opção 0 no menu principal.
    """
    while True:
        pyfiglet.print_figlet("Banco Pereira")
        input_utilizador = input(
            "Introduza um dos seguintes valores:\n"
            " 0 - Sair do programa\n"
            " 1 - Criar utilizador\n"
            " 2 - Entrar\n"
            "Valor Introduzido: "
        )

        if input_utilizador.isnumeric():
            match(int(input_utilizador)):
                case 0:
                    print("Sair do programa")
                    pyfiglet.print_figlet(". . . . . .")
                    break
                case 1:
                    try:
                        criar_utilizador()
                    except UtilizadorJaExisteError as username:
                        print(username)
                    except CampoVazio as campo:
                        print(campo)
                case 2:
                    try: 
                        user = entrar()
                    except UtilizadorInexistenteError as utilizador:
                        print(utilizador)
                    except CampoVazio as campo:
                        print(campo)
                    else:
                        while True:
                            pyfiglet.print_figlet("Conta")
                            input_utilizador2 = int(input(
                                "Introduza um dos seguintes valores:\n"
                                " 0 - Sair da conta\n"
                                " 3 - Depositar dinheiro\n"
                                " 4 - Consultar saldo\n"
                                " 5 - Transferir dinheiro\n"
                                " 6 - Consultar retorno\n"
                                " 7 - Gerar Relatório\n"
                                " 8 - Consultar Transferencias\n"
                                "Valor Introduzido: "
                            ))
                            match(input_utilizador2):
                                case 3:
                                    depositar(user)

                                case 4:
                                    print(consultar_saldo(user))

                                case 5:
                                    try:
                                        transferir(user,None,None)
                                    except SaldoInsuficienteError as saldo:
                                        print(saldo)
                                    except UtilizadorInexistenteError as utilizador:
                                        print(utilizador)
                                    except ProprioUtilizadorError as proprio:
                                        print(proprio)
                                case 6:
                                    print(
                                        "O valor com juro é:",
                                        consultar_retorno(
                                            numero_meses=None, taxa_juro=None, username=user
                                        )
                                    )
                                case 7:
                                    gerar_relatorios_em_paralelo()
                                case 8:
                                    consultar_transferencias(user)
                                case 0:
                                    print("Saiu da conta")
                                    break
                                case _:
                                    print("Opção inválida. Tente novamente.\n")
                case _:
                    print("Opção inválida. Tente novamente.\n")
        else:
            print("Não foi introduzido um numero")

if __name__ == "__main__":
    menu()
