from scipy.sparse.csgraph import csgraph_from_dense
import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS card (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0
    )
''')
conn.commit()


class Card:
    flag = True

    def __init__(self, card_number=None, pin=None, balance=0):
        self.card_number = card_number
        self.pin = pin
        self.balance = balance
        if Card.flag == True:
            self.menu()

    def menu(self):

        while Card.flag:
            print('1. Create an account')
            print('2. Log into account')
            print('0. Exit')
            choose_menu = input()
            if choose_menu == '1':
                self.create_an_account()
            if choose_menu == '2':
                self.verification()
            if choose_menu == '0':
                print('Bye!')
                Card.flag = False

    def create_an_account(self):

        def create_card(number=None):
            while True:
                number = '400000' + str(random.randint(int('0' * 10), int('9' * 10)))
                digits_sum = 0
                for i in range(len(number)):
                    if i % 2 == 0:
                        num = int(number[i]) * 2
                        if num > 9:
                            num -= 9
                        digits_sum += num
                    else:
                        digits_sum += int(number[i])
                checksum = (10 - digits_sum % 10) % 10
                if checksum % 10 == 0 and len(str(number)) == 15:
                    return str(number) + '0'

        def create_pin(pin=None):
            pin = random.randint(1111, 9999)
            return pin

        self.card_number = int(create_card())
        self.pin = create_pin()
        cur.execute(f'''INSERT INTO card (number, pin, balance)
                        VALUES ({self.card_number}, {self.pin}, {self.balance})''''')
        print('Your card has been created\nYour card number:')
        print(self.card_number)
        print('Your card PIN:')
        print(self.pin)
        conn.commit()

    def verification(self):
        chek_card = int(input('Enter your card number:\n'))
        chek_pin = int(input('Enter your PIN:\n'))
        cur.execute(f"SELECT * FROM card")
        db_card_results = cur.fetchall()
        sql_card = [i for i in [row[1] for row in db_card_results] if i == str(chek_card)]
        sql_pin = [i for i in [row[2] for row in db_card_results] if i == str(chek_pin)]
        if str(chek_card) in sql_card and str(chek_pin) in sql_pin:
            self.card_number = int(sql_card[0])
            self.pin = int(sql_pin[0])
            cur.execute(f"SELECT balance FROM card WHERE number = {str(self.card_number)}")
            db_balance = cur.fetchone()
            self.balance = db_balance[0]
            print('You have successfully logged in!')
            self.user_login()
        else:
            print('Wrong card number or PIN!')
            self.menu()

    def transfer(self):
        while True:
            print('Transfer')
            card_transfer = input('Enter card number:\n>')
            temp1 = list(card_transfer)
            temp2 = [int(temp1[x]) * 2 if x % 2 == 0 else int(temp1[x]) for x in range(len(temp1))]
            temp3 = [temp2[x] - 9 if temp2[x] > 9 else temp2[x] for x in range(len(temp2))]
            digit_sum = sum(temp3)
            if digit_sum % 10 != 0:
                print('Probably you made a mistake in the card number. Please try again!')
                continue

            if int(card_transfer) == self.card_number:
                print("You can't transfer money to the same account!")
                continue

            cur.execute(f"SELECT * FROM card")
            db_card_results = cur.fetchall()
            if card_transfer not in [i for i in [row[1] for row in db_card_results] if i == str(card_transfer)]:
                print('Such a card does not exist.')
                continue

            sum_transfer = int(input('Enter how much money you want to transfer:\n'))
            if sum_transfer > self.balance:
                print('Not enough money!')
                self.user_login()
                break

            if sum_transfer <= self.balance:
                self.balance -= sum_transfer
                cur.execute(f'SELECT balance FROM card WHERE number = {card_transfer}')
                db_transfer = cur.fetchone()
                transfer_balance = db_transfer[0] + sum_transfer
                cur.execute(f'UPDATE card SET balance = {self.balance}  WHERE number = {self.card_number}')
                cur.execute(f'UPDATE card SET balance = {transfer_balance}  WHERE number = {card_transfer}')
                conn.commit()
                print('Success!')
                self.user_login()
                break

    def user_login(self):
        while Card.flag:
            print('1. Balance')
            print('2. Add income')
            print('3. Do transfer')
            print('4. Close account')
            print('5. Log out')
            print('0. Exit')
            choose_user_login = input()
            if choose_user_login == '1':
                print(f'{self.balance}\n')
                self.user_login()
            if choose_user_login == '2':
                add_sum = int(input('Enter income:\n'))
                print('Income was added!')
                self.balance += add_sum
                cur.execute(f'UPDATE card SET balance = {self.balance} WHERE number = {str(self.card_number)}')
                conn.commit()
                self.user_login()
            if choose_user_login == '3':
                self.transfer()
            if choose_user_login == '4':

                cur.execute(f'DELETE FROM card WHERE number = {self.card_number}')
                conn.commit()
                print('The account has been closed!\n')
                self.menu()
            if choose_user_login == '5':
                print('You have successfully logged out!')
                self.menu()
            if choose_user_login == '0':
                print('Bye!')
                Card.flag = False



card = Card()

if Card.flag == True:
    print(card)

conn.close()
