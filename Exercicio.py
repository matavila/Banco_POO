from abc import ABC, abstractclassmethod , abstractproperty
from datetime import datetime

class Cliente():
    #Aqui iremos criar nossa classe que receberá nossas transações e também a parte de clientes (cadastro e conta)
    def __init__(self,nome,cpf):
        self.nome = nome 
        self.cpf = cpf
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self,conta):
        self.contas.append(conta)

class Pessoa_Fisica(Cliente):
    def __init__(self,nome,cpf , data_nascimento):
        super().__init__(nome,cpf)
        self.data_nascimento = data_nascimento

class Conta():
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico= Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico

    def Sacar(self,valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        #Aqui iremos verificar se o valor a ser retirado é maior que nosso saldo, se for menor e o valor ser positivo, então iremos realizar a operação de depositar
        #Após essa operaçao iremos retoranar para a parte da transação o valor true.
        if excedeu_saldo:
            print("X-------Operação Negada: Saldo Insuficiente---------X")
        elif valor > 0:
            self._saldo -= valor
            print("X-------Operação Realizada---------X")
            return True
        else:
            print("X-------Operação Negada: Valor Informado Invalido---------X")
        
        return False
        
    def Depositar(self,valor):
        #Aqui iremos verificar se o valor a depositar é maior que 0, caso seja verídico então iremos adicionar esse valor ou nosso saldo da conta.
        #Sendo feita essa operação de deposito, esse método irá retornar como verdadeiro para nosso método de transação
        if valor > 0:
            self._saldo += valor
            print("X-------Operação Realizada---------X")
        else:
            print("X-------Operação Negada: Valor Informado Invalido---------X")
            return False
        
        return True

class Conta_Corrente(Conta):
    def __init__(self, numero, cliente, limite = 500, limite_saque= 3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saque = limite_saque

    def Sacar(self,valor):
        numero_saque= len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saque >= self.limite_saque

        if excedeu_limite : 
            print("X-------Operação Negada: Limite de Saque Superado---------X")

        elif excedeu_saques: 
            print("X-------Operação Negada: Número de Saques Excessivos---------X")

        else:
            return super().Sacar(valor)
        
        return False
    
    def __str__(self):
        return f"""\
            Agência: \t {self.agencia}
            C|C: \t{self.numero}
            Titular: \t {self.cliente.nome}
        """
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
        
    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__ ,
            "valor": transacao.valor ,
            })

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass
    @abstractclassmethod
    def registrar(self,conta):
        pass

class Saque(Transacao):
    def __init__(self,valor):
        self._valor= valor 

    @property
    def valor(self):
        return self._valor
    
    def registrar(self,conta):
        sucesso_transacao = conta.Sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Depositar(Transacao):
    def __init__(self,valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self,conta):
        sucesso_transacao = conta.Depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(menu)


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Depositar(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
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


def exibir_extrato(clientes):
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
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    

    cliente = Pessoa_Fisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = Conta_Corrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(str(conta))


def main():
    clientes = []
    contas = []

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
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


main()