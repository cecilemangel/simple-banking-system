import random
import sqlite3


class Account:

    @staticmethod
    def get_card_checksum(card_number: str) -> int:
        numbers_sum = 0
        for index in range(15):
            number = int(card_number[index])
            if index % 2 == 0:
                number *= 2
            if number > 9:
                number -= 9
            numbers_sum += number
        numbers_sum %= 10
        checksum = 10 - numbers_sum
        return checksum % 10

    @staticmethod
    def generate() -> "Account":
        random_account_number = random.randint(0, 999999999)
        number_15 = "400000" + "%09d" % random_account_number
        number = number_15 + str(Account.get_card_checksum(number_15))
        pin = "%04d" % random.randint(0, 9999)
        return Account(number, pin)

    def __init__(self, _number: str, _pin: str):
        self.number = _number
        self.pin = _pin


class Database:

    def __init__(self, file_name: str):
        self.conn = sqlite3.connect(file_name)
        self.conn.execute("CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)")
        self.conn.commit()

    def insert_account(self, account: Account) -> None:
        self.conn.execute("INSERT INTO card VALUES (?, ?, ?, ?)",
                          (account.number, account.number, account.pin, 0))
        self.conn.commit()


    def check_login(self, number: str, pin: str) -> bool:
        c = self.conn.cursor()
        c.execute('SELECT number FROM card WHERE number = :number AND pin = :pin',
                  {"number": number, "pin": pin})
        return c.fetchone() is not None

    def get_balance(self, number: str) -> int:
        c = self.conn.cursor()
        c.execute('SELECT balance FROM card WHERE number = :number',
                  {"number": number})
        return c.fetchone()[0]

    def add_income(self, account: Account, income: int) -> None:
        self.conn.execute('UPDATE card SET balance = balance + :income WHERE id = :number',
                  {'income': income, 'number': account.number})
        self.conn.commit()

    def make_transfer(self, account: Account, account_to_transfer: str, amount: int) -> None:
        c = self.conn.cursor()
        c.execute('SELECT balance FROM card WHERE id = :number',
                  {"number": account.number})
        current_balance = c.fetchone()[0]

        if amount_to_transfer > current_balance:
            print("Not enough money!")
            return

        self.conn.execute('UPDATE card SET balance = balance - :amount WHERE id = :number',
                          {'amount': amount, 'number': account.number})
        self.conn.execute('UPDATE card SET balance = balance + :amount WHERE id = :number',
                          {'amount': amount, 'number': account_to_transfer})
        self.conn.commit()
        print("Success!")


    def account_exists(self, number: str) -> bool:
        c = self.conn.cursor()
        c.execute('SELECT number FROM card WHERE number = :number',
                  {"number": number})
        return c.fetchone() is not None

    def close_account(self, account: Account) -> None:
        self.conn.execute('DELETE FROM card WHERE number = :number',
                          {'number': account.number})
        self.conn.commit()
        print("The account has been closed!")

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

def login():  # -> Account
    print("Enter your card number:")
    input_card_number = input()

    print("Enter your PIN:")
    input_pin = input()

    if not db.check_login(input_card_number, input_pin):
        print("Wrong card number or PIN!")
        return None

    print("You have successfully logged in!")
    return Account(input_card_number, input_pin)



if __name__ == '__main__':
    db = Database('card.s3db')

    while True:
        print()
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        
        option = int(input())

        if option == 1:
            account = Account.generate()
            db.insert_account(account)
            print("Your card has been created")
            print("Your card number:")
            print(account.number)
            print("Your card PIN:")
            print(account.pin)

        elif option == 2:
            account = login()
            if account is None:
                continue

            while True:
                print()
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")

                logged_option = int(input())

                if logged_option == 1:
                    balance = db.get_balance(account.number)
                    print(f"Balance: {balance}")

                elif logged_option == 2:
                    print("Enter income:")
                    income_to_add = int(input())
                    db.add_income(account, income_to_add)
                    print("Income was added!")

                elif logged_option == 3:
                    print("Transfer")

                    print("Enter card number:")
                    account_to_transfer = input()
                    if account_to_transfer == account.number:
                        print("You can't transfer money to the same account!")
                        continue
                    if Account.get_card_checksum(account_to_transfer) != int(account_to_transfer[-1:]):
                        print("Probably you made mistake in the card number. Please try again!")
                        continue
                    if not db.account_exists(account_to_transfer):
                        print("Such a card does not exist.")
                        continue

                    print("Enter how much money you want to transfer:")
                    amount_to_transfer = int(input())
                    db.make_transfer(account, account_to_transfer, amount_to_transfer)

                elif logged_option == 4:
                    db.close_account(account)
                    break

                elif logged_option == 5:
                    print("You have successfully logged out!")
                    break

                elif logged_option == 0:
                    db.close()
                    exit(0)

        elif option == 0:
            print("Bye!")
            break

    db.close()

