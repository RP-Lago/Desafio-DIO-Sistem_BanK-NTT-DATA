import textwrap
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
import requests
from typing import List, Optional
import functools
import unittest

# config.py
LIMITE_PADRAO = 500
LIMITE_SAQUES_PADRAO = 3
ARQUIVO_DADOS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "banco_de_dados_bank.json"
)


def log_transaction(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Descrição da transação: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Transação efetuada: {func.__name__}")
        return result

    return wrapper


class Cliente:
    """
    Representa um cliente do banco.

    Atributos:
        endereco (str): Endereço do cliente.
        contas (List[Conta]): Lista de contas do cliente.
    """

    def __init__(self, endereco: str, contas: Optional[List["Conta"]] = None):
        self.endereco = endereco
        self.contas = contas or []

    def realizar_transacao(self, conta: "Conta", transacao: "Transacao") -> None:
        """
        Realiza uma transação em uma conta do cliente.

        Args:
            conta (Conta): Conta em que a transação será realizada.
            transacao (Transacao): Transação a ser realizada.
        """
        transacao.registrar(conta)

    def adicionar_conta(self, conta: "Conta") -> None:
        """
        Adiciona uma nova conta ao cliente.

        Args:
            conta (Conta): Conta a ser adicionada.
        """
        self.contas.append(conta)


class PessoaFisica(Cliente):
    """
    Representa um cliente pessoa física.

    Atributos:
        nome (str): Nome do cliente.
        data_nascimento (str): Data de nascimento do cliente.
        cpf (str): CPF do cliente.
        endereco (str): Endereço do cliente.
    """

    def __init__(self, nome: str, data_nascimento: str, cpf: str, endereco: str):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    def to_dict(self) -> dict:
        """
        Converte o objeto PessoaFisica para um dicionário.

        Returns:
            dict: Representação do objeto em formato de dicionário.
        """
        return {
            "nome": self.nome,
            "data_nascimento": self.data_nascimento,
            "cpf": self.cpf,
            "endereco": self.endereco,
            "contas": [conta.numero for conta in self.contas],
        }


class Conta:
    """
    Representa uma conta bancária genérica.

    Atributos:
        numero (str): Número da conta.
        cliente (Cliente): Cliente dono da conta.
        saldo (float): Saldo atual da conta.
        agencia (str): Número da agência.
        historico (Historico): Histórico de transações da conta.
    """

    def __init__(self, numero: str, cliente: Cliente, saldo: float = 0):
        self._saldo = saldo
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: str, saldo: float = 0) -> "Conta":
        """
        Cria uma nova conta.

        Args:
            cliente (Cliente): Cliente dono da conta.
            numero (str): Número da conta.
            saldo (float, opcional): Saldo inicial da conta. Padrão é 0.

        Returns:
            Conta: Nova instância de Conta.
        """
        return cls(numero, cliente, saldo)

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def numero(self) -> str:
        return self._numero

    @property
    def agencia(self) -> str:
        return self._agencia

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def historico(self) -> "Historico":
        return self._historico

    def _realizar_operacao(self, valor: float, tipo_operacao: str) -> bool:
        """
        Método genérico para realizar operações de depósito e saque.

        Args:
            valor (float): Valor da operação.
            tipo_operacao (str): Tipo de operação ('saque' ou 'deposito').

        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário.
        """
        if valor > 0:
            if tipo_operacao == "saque":
                self._saldo -= valor
            elif tipo_operacao == "deposito":
                self._saldo += valor
            print(f"\n=== {tipo_operacao.capitalize()} realizado com sucesso! ===")
            return True
        else:
            print(
                f"\n@@@ Operação de {tipo_operacao} falhou! O valor informado é inválido. @@@"
            )
            return False

    def sacar(self, valor: float) -> bool:
        """
        Realiza um saque na conta.

        Args:
            valor (float): Valor a ser sacado.

        Returns:
            bool: True se o saque foi bem-sucedido, False caso contrário.
        """
        if valor > self.saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False
        return self._realizar_operacao(valor, "saque")

    def depositar(self, valor: float) -> bool:
        """
        Realiza um depósito na conta.

        Args:
            valor (float): Valor a ser depositado.

        Returns:
            bool: True se o depósito foi bem-sucedido, False caso contrário.
        """
        return self._realizar_operacao(valor, "deposito")


class ContaCorrente(Conta):
    """
    Representa uma conta corrente no sistema bancário.

    Atributos:
        numero (str): Número da conta.
        cliente (Cliente): Cliente associado à conta.
        limite (float): Limite de saque da conta.
        limite_saques (int): Número máximo de saques permitidos.
        saldo (float): Saldo atual da conta.
    """

    def __init__(
        self,
        numero: str,
        cliente: Cliente,
        limite: float = LIMITE_PADRAO,
        limite_saques: int = LIMITE_SAQUES_PADRAO,
        saldo: float = 0,
    ):
        super().__init__(numero, cliente, saldo)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor: float) -> bool:
        """
        Realiza um saque na conta corrente.

        Args:
            valor (float): Valor a ser sacado.

        Returns:
            bool: True se o saque foi bem-sucedido, False caso contrário.
        """
        numero_saques = len(
            [
                transacao
                for transacao in self.historico.transacoes
                if transacao["tipo"] == Saque.__name__
            ]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False

        if excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self) -> str:
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

    def to_dict(self) -> dict:
        """
        Converte o objeto ContaCorrente para um dicionário.

        Returns:
            dict: Representação do objeto em formato de dicionário.
        """
        return {
            "numero": self.numero,
            "agencia": self.agencia,
            "saldo": self.saldo,
            "cliente_cpf": self.cliente.cpf,
            "limite": self._limite,
            "limite_saques": self._limite_saques,
            "historico": self.historico.transacoes,
        }


class Historico:
    """
    Representa o histórico de transações de uma conta.

    Atributos:
        transacoes (List[dict]): Lista de transações realizadas.
    """

    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self) -> List[dict]:
        return self._transacoes

    def adicionar_transacao(self, transacao: "Transacao") -> None:
        """
        Adiciona uma nova transação ao histórico.

        Args:
            transacao (Transacao): Transação a ser adicionada.
        """
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transacao(ABC):
    """Classe abstrata que representa uma transação bancária."""

    @property
    @abstractmethod
    def valor(self) -> float:
        """Valor da transação."""
        pass

    @abstractmethod
    def registrar(self, conta: Conta) -> None:
        """
        Registra a transação em uma conta.

        Args:
            conta (Conta): Conta em que a transação será registrada.
        """
        pass


class Saque(Transacao):
    """Representa uma transação de saque."""

    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: Conta) -> None:
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    """Representa uma transação de depósito."""

    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: Conta) -> None:
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu() -> str:
    """
    Exibe o menu de opções e retorna a escolha do usuário.

    Returns:
        str: Opção escolhida pelo usuário.
    """
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [b]\tSalvar Dados
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def carregar_dados() -> dict:
    """
    Carrega os dados do arquivo JSON.

    Returns:
        dict: Dados carregados do arquivo.
    """
    print("Carregando dados de:", ARQUIVO_DADOS)  # Mensagem de depuração

    try:
        with open(ARQUIVO_DADOS, "r") as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        print("Arquivo JSON não encontrado. Criando um novo arquivo.")
        dados = {"clientes": [], "contas": [], "proximo_numero_conta": 1}
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON. Criando um novo arquivo.")
        dados = {"clientes": [], "contas": [], "proximo_numero_conta": 1}

    clientes_dict = {}
    contas_dict = {}

    for cliente_data in dados.get("clientes", []):
        cliente = PessoaFisica(
            nome=cliente_data["nome"],
            data_nascimento=cliente_data["data_nascimento"],
            cpf=cliente_data["cpf"],
            endereco=cliente_data["endereco"],
        )
        clientes_dict[cliente.cpf] = cliente

    # Carregue as contas e associe-as aos clientes
    for conta_data in dados.get("contas", []):
        cliente_cpf = conta_data["cliente_cpf"]
        cliente = clientes_dict.get(cliente_cpf)

        if cliente:
            conta = ContaCorrente(
                numero=conta_data["numero"],
                cliente=cliente,
                saldo=conta_data["saldo"],
                limite=conta_data["limite"],
                limite_saques=conta_data["limite_saques"],
            )
            conta._historico = Historico()
            for transacao_data in conta_data["historico"]:
                if transacao_data["tipo"] == "Saque":
                    transacao = Saque(transacao_data["valor"])
                elif transacao_data["tipo"] == "Deposito":
                    transacao = Deposito(transacao_data["valor"])
                else:
                    continue
                conta._historico.adicionar_transacao(transacao)
            contas_dict[conta.numero] = conta
            cliente.adicionar_conta(conta)

    # Converta os dicionários de clientes e contas de volta para listas
    clientes = list(clientes_dict.values())
    contas = list(contas_dict.values())

    dados["clientes"] = clientes
    dados["contas"] = contas

    return dados


def salvar_dados(dados: dict) -> None:
    """
    Salva os dados dos clientes em um arquivo JSON.

    Args:
        dados (dict): Dados a serem salvos.
    """
    print("Salvando dados em:", ARQUIVO_DADOS)  # Mensagem de depuração

    try:
        with open(ARQUIVO_DADOS, "w") as arquivo:
            json.dump(dados, arquivo, indent=4, default=lambda o: o.to_dict())
        print("Dados salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar os dados: {e}")


def filtrar_cliente(cpf: str, clientes: List[PessoaFisica]) -> Optional[PessoaFisica]:
    """
    Filtra um cliente pelo CPF.

    Args:
        cpf (str): CPF do cliente a ser filtrado.
        clientes (List[PessoaFisica]): Lista de clientes.

    Returns:
        Optional[PessoaFisica]: Cliente encontrado ou None se não encontrado.
    """
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente: PessoaFisica) -> Optional[Conta]:
    """
    Recupera uma conta do cliente.

    Args:
        cliente (PessoaFisica): Cliente dono da conta.

    Returns:
        Optional[Conta]: Conta recuperada ou None se o cliente não possuir contas.
    """
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    print("Contas disponíveis:")
    for i, conta in enumerate(cliente.contas):
        print(f"[{i + 1}] Agência: {conta.agencia}, Conta: {conta.numero}")

    while True:
        opcao_conta = input("Digite o número da conta desejada: ").strip()

        # Se o número da conta no JSON é uma string, compare como string
        for conta in cliente.contas:
            if opcao_conta == conta.numero:  # Aqui a comparação é feita com o número da conta
                return conta
        
        print("Opção inválida. Digite um número válido.")


    return None

@log_transaction
def depositar(clientes: List[PessoaFisica]) -> None:
    """
    Realiza um depósito em uma conta.

    Args:
        clientes (List[PessoaFisica]): Lista de clientes.
    """
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transaction
def sacar(clientes: List[PessoaFisica]) -> None:
    """
    Realiza um saque em uma conta.

    Args:
        clientes (List[PessoaFisica]): Lista de clientes.
    """
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes: List[PessoaFisica]) -> None:
    """
    Exibe o extrato de uma conta.

    Args:
        clientes (List[PessoaFisica]): Lista de clientes.
    """
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f} - {transacao['data']}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


def criar_cliente(clientes: List[PessoaFisica]) -> None:
    """
    Cria um novo cliente.

    Args:
        clientes (List[PessoaFisica]): Lista de clientes existentes.
    """
    cpf = input("Informe o CPF (somente número): ")
    if not cpf.isdigit() or len(cpf) != 11:
        print("CPF inválido. Digite apenas 11 números.")
        return

    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")

    while True:
        data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
        try:
            datetime.strptime(data_nascimento, "%d-%m-%Y")
            break  # Sai do loop se a data for válida
        except ValueError:
            print("Data de nascimento inválida. Utilize o formato dd-mm-aaaa.")

    while True:
        cep = input("Informe o CEP (somente números): ")
        if len(cep) == 8:
            endereco = buscar_endereco_por_cep(cep)
            if endereco:
                print(f"Endereço encontrado: {endereco}")
                numero = input("Informe o número: ")
                endereco_completo = f"{endereco}, {numero}"
                break
            else:
                print("CEP não encontrado. Tente novamente.")
        else:
            print("CEP inválido. Digite um CEP com 8 dígitos.")

    cliente = PessoaFisica(
        nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco_completo
    )

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


def buscar_endereco_por_cep(cep: str) -> Optional[str]:
    """
    Busca o endereço a partir de um CEP usando a API ViaCEP.

    Args:
        cep (str): CEP a ser consultado.

    Returns:
        Optional[str]: Endereço encontrado ou None se não encontrado.
    """
    try:
        url = f"https://viacep.com.br/ws/{cep}/json/"
        resposta = requests.get(url, timeout=5)
        resposta.raise_for_status()
        dados_endereco = resposta.json()
        if "erro" not in dados_endereco:
            return f"{dados_endereco['logradouro']}, {dados_endereco['bairro']} - {dados_endereco['localidade']}/{dados_endereco['uf']}"
    except requests.RequestException as e:
        print(f"Erro ao buscar CEP: {e}")
    except json.JSONDecodeError:
        print("Erro ao decodificar resposta JSON")
    return None


def criar_conta(numero_conta: int, clientes: List[PessoaFisica], contas: List[Conta]) -> None:
    """
    Cria uma nova conta para um cliente existente.

    Args:
        numero_conta (int): Número da nova conta.
        clientes (List[PessoaFisica]): Lista de clientes existentes.
        contas (List[Conta]): Lista de contas existentes.
    """
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    saldo_inicial = float(input("Deseja adicionar um saldo inicial? (0 para não): "))

    conta = ContaCorrente.nova_conta(
        cliente=cliente, numero=str(numero_conta), saldo=saldo_inicial
    )
    if saldo_inicial > 0:
        deposito_inicial = Deposito(saldo_inicial)
        deposito_inicial.registrar(conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas: List[Conta]) -> None:
    """
    Lista todas as contas cadastradas.

    Args:
        contas (List[Conta]): Lista de contas existentes.
    """
    if not contas:
        print("\n@@@ Não há contas cadastradas. @@@")
        return

    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    """Função principal do programa."""
    dados = carregar_dados()
    clientes = dados["clientes"]
    contas = dados["contas"]
    proximo_numero_conta = dados.get("proximo_numero_conta", 1)

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            criar_conta(proximo_numero_conta, clientes, contas)
            proximo_numero_conta += 1

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "b":  # Opção para salvar os dados
            dados["clientes"] = clientes  # Atualiza a lista de clientes
            dados["contas"] = contas  # Atualiza a lista de contas
            dados["proximo_numero_conta"] = proximo_numero_conta
            salvar_dados(dados)
            print("\n=== Dados salvos com sucesso! ===")

        elif opcao == "q":
            dados["clientes"] = clientes
            dados["contas"] = contas
            dados["proximo_numero_conta"] = proximo_numero_conta
            salvar_dados(dados)
            break

        else:
            print(
                "\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@"
            )


class TestContaCorrente(unittest.TestCase):
    """Testes unitários para a classe ContaCorrente."""

    def setUp(self):
        self.cliente = PessoaFisica(
            "João", "01-01-1990", "12345678901", "Rua A, 123"
        )
        self.conta = ContaCorrente(
            "1234", self.cliente, limite=1000, limite_saques=5
        )

    def test_saque_dentro_do_limite(self):
        self.conta.depositar(500)
        self.assertTrue(self.conta.sacar(300))
        self.assertEqual(self.conta.saldo, 200)

    def test_saque_acima_do_limite(self):
        self.conta.depositar(500)
        self.assertFalse(self.conta.sacar(1200))
        self.assertEqual(self.conta.saldo, 500)


if __name__ == "__main__":
    main()