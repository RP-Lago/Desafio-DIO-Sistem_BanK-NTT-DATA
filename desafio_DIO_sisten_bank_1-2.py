from abc import ABC, abstractmethod
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        )

class Conta(ABC):
    def __init__(self, numero, cliente):
        self._saldo = 0
        self.numero = numero
        self.agencia = "0001"
        self.cliente = cliente
        self.historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @abstractmethod
    def sacar(self, valor):
        pass

    @abstractmethod
    def depositar(self, valor):
        pass

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        if valor <= 0:
            print("\n@@@ Operação não realizada. Valor inválido. @@@")
            return False
        elif valor > self.saldo:
            print("\n@@@ Operação não realizada. Saldo insuficiente. @@@")
            return False
        else:
            self._saldo -= valor
            print("\n=== Operação realizada com sucesso. ===")
            return True

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Operação realizada com sucesso. ===")
            return True
        else:
            print("\n@@@ Operação não realizada. Valor inválido. @@@")
            return False

class Transacao(ABC):
    def __init__(self, valor):
        self.valor = valor

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def registrar(self, conta):
        conta.sacar(self.valor)

class Deposito(Transacao):
    def registrar(self, conta):
        conta.depositar(self.valor)
