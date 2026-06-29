import os
import json
import time
from datetime import datetime, date
import hashlib

class Atm:
    def __init__(self):
        self.file_path = 'data/users.json'
        self.users = self.load_users()
        self.account_no = 5000000

    def load_users(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
            return {}
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def save_users(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.users, f, indent=4)

    def hash_pin(self, pin):
        return hashlib.sha256(str(pin).encode()).hexdigest()

    # ---------------- CREATE ACCOUNT ----------------
    def create_account(self, name, pin, balance, answer):
        self.account_no += 1
        acc = str(self.account_no)

        self.users[acc] = {
            'name': name,
            'pin': self.hash_pin(pin),
            'balance': balance,
            'transactions': [],
            'transfer_transactions': [],
            'failed_attempts': 0,
            'is_locked': False,
            'lock_time': None,
            'withdraw_limit': 20000,
            'deposit_limit': 20000,
            'transfer_limit': 10000,
            'security_answer': answer.lower()
        }

        self.save_users()
        return acc

    # ---------------- LOGIN ----------------
    def login(self, acc, pin):
        if acc not in self.users:
            return False, "Account not found"

        user = self.users[acc]

        if user['is_locked']:
            if time.time() - user['lock_time'] < 60:
                return False, "Account locked. Try later"
            else:
                user['is_locked'] = False
                user['failed_attempts'] = 0

        if self.hash_pin(pin) == user['pin']:
            user['failed_attempts'] = 0
            self.save_users()
            return True, "Login success"

        else:
            user['failed_attempts'] += 1
            if user['failed_attempts'] > 3:
                user['is_locked'] = True
                user['lock_time'] = time.time()
            self.save_users()
            return False, "Wrong PIN"

    # ---------------- BALANCE ----------------
    def get_balance(self, acc):
        return self.users[acc]['balance']

    # ---------------- DEPOSIT ----------------
    def deposit(self, acc, amount):
        user = self.users[acc]
        user['balance'] += amount

        user['transactions'].append({
            'type': 'deposit',
            'amount': amount,
            'timestamp': str(datetime.now())
        })

        self.save_users()
        return True, "Deposited"

    # ---------------- WITHDRAW ----------------
    def withdraw(self, acc, amount):
        user = self.users[acc]

        if amount > user['balance']:
            return False, "Insufficient balance"

        user['balance'] -= amount
        user['transactions'].append({
            'type': 'withdraw',
            'amount': amount,
            'timestamp': str(datetime.now())
        })

        self.save_users()
        return True, "Withdraw successful"

    # ---------------- TRANSFER ----------------
    def transfer(self, sender, receiver, amount):
        if receiver not in self.users:
            return False, "Receiver not found"

        if sender == receiver:
            return False, "Same account"

        if amount > self.users[sender]['balance']:
            return False, "Insufficient balance"

        self.users[sender]['balance'] -= amount
        self.users[receiver]['balance'] += amount

        self.save_users()
        return True, "Transfer successful"

    # ---------------- HISTORY ----------------
    def get_transactions(self, acc):
        return self.users[acc]['transactions']