
import tkinter as tk
from tkinter import messagebox
import json
import os
import hashlib

BALANCE_FILE = "wallet_balance.json"
HASH_FILE = "wallet_hash.json"

def load_balance():
    try:
        with open(BALANCE_FILE, "r") as file:
            balance = json.load(file)
        verify_balance_integrity(balance)
        return balance
    except FileNotFoundError:
        return {}

def save_balance(balance):
    with open(BALANCE_FILE, "w") as file:
        json.dump(balance, file)
    save_balance_hash(balance)

def save_balance_hash(balance):
    hash_value = hashlib.sha256(json.dumps(balance, sort_keys=True).encode()).hexdigest()
    with open(HASH_FILE, "w") as file:
        file.write(hash_value)

def verify_balance_integrity(balance):
    try:
        with open(HASH_FILE, "r") as file:
            stored_hash = file.read()
        current_hash = hashlib.sha256(json.dumps(balance, sort_keys=True).encode()).hexdigest()
        if stored_hash != current_hash:
            raise ValueError("Balance file integrity check failed!")
    except FileNotFoundError:
        print("No hash file found. Assuming first-time initialization.")

def create_wallet():
    wallet_address = "WALLET-" + os.urandom(16).hex()
    balance = load_balance()
    balance[wallet_address] = 0.0
    save_balance(balance)
    messagebox.showinfo("Wallet Created", f"Your new wallet address is: {wallet_address}")

def show_balance():
    balance = load_balance()
    wallet_address = wallet_address_entry.get()
    if wallet_address in balance:
        messagebox.showinfo("Balance", f"Wallet Balance: {balance[wallet_address]} LMC")
    else:
        messagebox.showerror("Error", "Wallet address not found.")

def send_lmc():
    balance = load_balance()
    wallet_address = wallet_address_entry.get()
    recipient_address = recipient_address_entry.get()
    amount = float(amount_entry.get())

    if wallet_address in balance and balance[wallet_address] >= amount:
        balance[wallet_address] -= amount
        if recipient_address in balance:
            balance[recipient_address] += amount
        else:
            balance[recipient_address] = amount
        save_balance(balance)
        messagebox.showinfo("Transaction Success", "LMC sent successfully!")
    else:
        messagebox.showerror("Error", "Insufficient balance or invalid wallet address.")

root = tk.Tk()
root.title("LMC Wallet")

tk.Label(root, text="Your Wallet Address:").grid(row=0, column=0, padx=10, pady=10)
wallet_address_entry = tk.Entry(root, width=50)
wallet_address_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Recipient Address:").grid(row=1, column=0, padx=10, pady=10)
recipient_address_entry = tk.Entry(root, width=50)
recipient_address_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Amount:").grid(row=2, column=0, padx=10, pady=10)
amount_entry = tk.Entry(root, width=20)
amount_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Button(root, text="Create Wallet", command=create_wallet).grid(row=3, column=0, pady=10)
tk.Button(root, text="Check Balance", command=show_balance).grid(row=3, column=1, pady=10)
tk.Button(root, text="Send LMC", command=send_lmc).grid(row=3, column=2, pady=10)

root.mainloop()
