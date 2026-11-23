# Python_Multibanco_Firebase
Máquina de multibanco com persistência de dados numa base de dados noSQL desenvolvido em âmbito de CET

# Banco Pereira

Aplicação bancária de consola, escrita em Python, que guarda os dados no **Firebase Firestore**. Cada utilizador pode criar uma conta, entrar, depositar dinheiro, consultar o saldo, transferir dinheiro para outros utilizadores, simular juros compostos e consultar o seu histórico de transferências. Também há relatórios globais, gerados em paralelo com `multiprocessing`.

## Funcionalidades

**Menu principal**

| Opção | Ação |
|---|---|
| 0 | Sair do programa |
| 1 | Criar utilizador |
| 2 | Entrar |

**Menu da conta** (depois de entrar)

| Opção | Ação |
|---|---|
| 0 | Sair da conta |
| 3 | Depositar dinheiro |
| 4 | Consultar saldo |
| 5 | Transferir dinheiro para outro utilizador |
| 6 | Consultar retorno com juro composto (1 a 12 meses, taxa de 0 a 100%) |
| 7 | Gerar relatórios de saldos e de transferências (em paralelo) |
| 8 | Consultar as transferências do utilizador |

**Regras de validação**

- O username não pode estar vazio nem já existir.
- A password tem de ter entre 6 e 10 caracteres, com pelo menos uma letra e um número.
- Depósitos e transferências têm de ser maiores que 0.
- Não é possível transferir para a própria conta, para uma conta que não existe, nem um valor superior ao saldo.
- As transferências são feitas numa **transação do Firestore**: ou todas as alterações são aplicadas (débito, crédito e registo), ou nenhuma é.

## Estrutura do projeto

```
ProjetoLinguagemComplexa/
├── projeto_final.py              # Ponto de entrada: menus da aplicação
├── ligacao_base_dados.py         # Ligação ao Firebase (cria o cliente `db`)
├── chave.json                    # Chave da conta de serviço do Firebase (NÃO partilhar)
├── texto.json                    # Dados de exemplo antigos (não usados pelo código atual)
├── ModulosProjeto/
│   └── pacotes/
│       ├── modulos_criacao_e_entrada.py   # Criar utilizador e entrar
│       ├── modulos_funcoes_no_banco.py    # Depositar, saldo, juros, transferências
│       ├── modulos_relatorios.py          # Relatórios e histórico de transferências
│       └── modulos_excecoes.py            # Exceções personalizadas
└── tests/
    └── test_module.py            # Testes com pytest (base de dados simulada)
```

## Requisitos

- **Python 3.12 ou superior** (o código usa `match`/`case` e f-strings com aspas duplas aninhadas, que só funcionam a partir do 3.12)
- Um projeto Firebase com o **Cloud Firestore** ativo
- Pacotes Python:
  - `firebase-admin`
  - `pyfiglet`
  - `pytest` (só para os testes)

## Instalação

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install firebase-admin pyfiglet pytest
```

## Configuração do Firebase

1. Na consola do Firebase, abra **Definições do projeto → Contas de serviço** e gere uma nova chave privada.
2. Guarde o ficheiro descarregado na raiz do projeto com o nome `chave.json`.

O programa tem de ser executado a partir da raiz do projeto, porque `ligacao_base_dados.py` procura o `chave.json` na pasta atual.

### Coleções no Firestore

**`utilizadores`** (o ID de cada documento é o username)

| Campo | Tipo | Descrição |
|---|---|---|
| `Username` | string | Nome do utilizador |
| `Password` | string | Password (guardada em texto simples) |
| `Saldo` | number | Saldo da conta |

**`transferencias`** (ID gerado automaticamente)

| Campo | Tipo | Descrição |
|---|---|---|
| `Data` | string | Data e hora no formato `AAAA-MM-DD HH:MM:SS` |
| `Valor` | number | Quantia transferida |
| `Origem` | reference | Documento do utilizador que enviou |
| `Destino` | reference | Documento do utilizador que recebeu |

A opção 8 (consultar transferências) usa uma consulta com `OR` e `order_by("Data")`. Na primeira execução, o Firestore pode pedir para criar um índice; nesse caso, basta abrir o link que aparece na mensagem de erro.

## Execução

```bash
python projeto_final.py
```

## Testes

Os testes usam `pytest` e `unittest.mock` para substituir a base de dados por uma falsa, por isso não alteram dados reais. Cobrem:

- criar um utilizador com um username que já existe;
- transferir para um utilizador que não existe;
- uma transferência com sucesso;
- transferir com saldo insuficiente.

```bash
python -m pytest
```

Nota: ao importar os módulos, `ligacao_base_dados.py` liga-se logo ao Firebase, por isso o `chave.json` tem de existir mesmo para correr os testes.

## Exceções personalizadas

Definidas em `modulos_excecoes.py`:

| Exceção | Quando é levantada |
|---|---|
| `UtilizadorJaExisteError` | Criar um utilizador com um username que já existe |
| `UtilizadorInexistenteError` | Entrar com dados errados ou transferir para uma conta que não existe |
| `SaldoInsuficienteError` | Transferir mais do que o saldo disponível |
| `ProprioUtilizadorError` | Transferir para a própria conta |
| `CampoVazio` | Deixar o username vazio |
