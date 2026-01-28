import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


class Customer:
    def __init__(self, address):
        self.address = address
        self.accounts = []

    def perform_transaction(self, account, transaction):
        transaction.register(account)

    def add_account(self, account):
        self.accounts.append(account)


class NaturalPerson(Customer):
    def __init__(self, name, date_of_birth, cpf, address):
        super().__init__(address)
        self.name = name
        self.date_of_birth = date_of_birth
        self.cpf = cpf


class Account:
    def __init__(self, number, customer):
        self._balance = 0
        self._number = number
        self._branch = "0001"
        self._customer = customer
        self._history = History()

    @classmethod
    def new_account(cls, customer, number):
        return cls(number, customer)

    @property
    def balance(self):
        return self._balance

    @property
    def number(self):
        return self._number

    @property
    def branch(self):
        return self._branch

    @property
    def customer(self):
        return self._customer

    @property
    def history(self):
        return self._history

    def withdraw(self, amount):
        balance = self.balance
        exceeded_balance = amount > balance

        if exceeded_balance:
            print("\n@@@ Operation failed! You do not have enough balance. @@@")

        elif amount > 0:
            self._balance -= amount
            print("\n=== Withdrawal successful! ===")
            return True

        else:
            print("\n@@@ Operation failed! The amount is invalid. @@@")

        return False

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            print("\n=== Deposit successful! ===")
        else:
            print("\n@@@ Operation failed! The amount is invalid. @@@")
            return False

        return True


class CheckingAccount(Account):
    def __init__(self, number, customer, limit=500, withdrawal_limit=3):
        super().__init__(number, customer)
        self._limit = limit
        self._withdrawal_limit = withdrawal_limit

    def withdraw(self, amount):
        number_of_withdrawals = len(
            [trans for trans in self.history.transactions if trans["type"] == Withdrawal.__name__]
        )

        exceeded_limit = amount > self._limit
        exceeded_withdrawals = number_of_withdrawals >= self._withdrawal_limit

        if exceeded_limit:
            print("\n@@@ Operation failed! The withdrawal amount exceeds the limit. @@@")

        elif exceeded_withdrawals:
            print("\n@@@ Operation failed! Maximum number of withdrawals exceeded. @@@")

        else:
            return super().withdraw(amount)

        return False

    def __str__(self):
        return f"""\
            Branch:\t{self.branch}
            Account:\t{self.number}
            Holder:\t{self.customer.name}
        """


class History:
    def __init__(self):
        self._transactions = []

    @property
    def transactions(self):
        return self._transactions

    def add_transaction(self, transaction):
        self._transactions.append(
            {
                "type": transaction.__class__.__name__,
                "amount": transaction.amount,
                "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transaction(ABC):
    @property
    @abstractproperty
    def amount(self):
        pass

    @abstractclassmethod
    def register(self, account):
        pass


class Withdrawal(Transaction):
    def __init__(self, amount):
        self._amount = amount

    @property
    def amount(self):
        return self._amount

    def register(self, account):
        success_transaction = account.withdraw(self.amount)

        if success_transaction:
            account.history.add_transaction(self)


class Deposit(Transaction):
    def __init__(self, amount):
        self._amount = amount

    @property
    def amount(self):
        return self._amount

    def register(self, account):
        success_transaction = account.deposit(self.amount)

        if success_transaction:
            account.history.add_transaction(self)


def menu():
    menu_text = """\n
    ================ MENU ================
    [d]\tDeposit
    [w]\tWithdraw
    [s]\tStatement
    [na]\tNew Account
    [la]\tList Accounts
    [nu]\tNew User
    [q]\tQuit
    => """
    return input(textwrap.dedent(menu_text))


def filter_customer(cpf, customers):
    filtered_customers = [customer for customer in customers if customer.cpf == cpf]
    return filtered_customers[0] if filtered_customers else None


def recover_customer_account(customer):
    if not customer.accounts:
        print("\n@@@ Customer does not have an account! @@@")
        return

    # FIXME: does not allow customer to choose the account
    return customer.accounts[0]


def deposit(customers):
    cpf = input("Enter the customer CPF: ")
    customer = filter_customer(cpf, customers)

    if not customer:
        print("\n@@@ Customer not found! @@@")
        return

    amount = float(input("Enter the deposit amount: "))
    transaction = Deposit(amount)

    account = recover_customer_account(customer)
    if not account:
        return

    customer.perform_transaction(account, transaction)


def withdraw(customers):
    cpf = input("Enter the customer CPF: ")
    customer = filter_customer(cpf, customers)

    if not customer:
        print("\n@@@ Customer not found! @@@")
        return

    amount = float(input("Enter the withdrawal amount: "))
    transaction = Withdrawal(amount)

    account = recover_customer_account(customer)
    if not account:
        return

    customer.perform_transaction(account, transaction)


def display_statement(customers):
    cpf = input("Enter the customer CPF: ")
    customer = filter_customer(cpf, customers)

    if not customer:
        print("\n@@@ Customer not found! @@@")
        return

    account = recover_customer_account(customer)
    if not account:
        return

    print("\n================ STATEMENT ================")
    transactions = account.history.transactions

    statement = ""
    if not transactions:
        statement = "No transactions found."
    else:
        for transaction in transactions:
            statement += f"\n{transaction['type']}:\n\t$ {transaction['amount']:.2f}"

    print(statement)
    print(f"\nBalance:\n\t$ {account.balance:.2f}")
    print("===========================================")


def create_customer(customers):
    cpf = input("Enter CPF (numbers only): ")
    customer = filter_customer(cpf, customers)

    if customer:
        print("\n@@@ A customer with this CPF already exists! @@@")
        return

    name = input("Enter full name: ")
    date_of_birth = input("Enter date of birth (dd-mm-yyyy): ")
    address = input("Enter address (street, no - neighborhood - city/state): ")

    customer = NaturalPerson(name=name, date_of_birth=date_of_birth, cpf=cpf, address=address)

    customers.append(customer)

    print("\n=== Customer created successfully! ===")


def create_account(account_number, customers, accounts):
    cpf = input("Enter the customer CPF: ")
    customer = filter_customer(cpf, customers)

    if not customer:
        print("\n@@@ Customer not found, account creation flow terminated! @@@")
        return

    account = CheckingAccount.new_account(customer=customer, number=account_number)
    accounts.append(account)
    customer.accounts.append(account)

    print("\n=== Account created successfully! ===")


def list_accounts(accounts):
    for account in accounts:
        print("=" * 100)
        print(textwrap.dedent(str(account)))


def main():
    customers = []
    accounts = []

    while True:
        option = menu()

        if option == "d":
            deposit(customers)

        elif option == "w": # Changed from 's' (sacar) to 'w' (withdraw)
            withdraw(customers)

        elif option == "s": # Changed from 'e' (extrato) to 's' (statement)
            display_statement(customers)

        elif option == "nu":
            create_customer(customers)

        elif option == "na": # Changed from 'nc' (nova conta) to 'na' (new account)
            account_number = len(accounts) + 1
            create_account(account_number, customers, accounts)

        elif option == "la": # Changed from 'lc' (listar contas) to 'la' (list accounts)
            list_accounts(accounts)

        elif option == "q":
            break

        else:
            print("\n@@@ Invalid operation, please select the desired operation again. @@@")


main()