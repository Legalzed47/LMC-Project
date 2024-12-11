
import os
import hashlib
import json
import secrets
from tkinter import Tk, Label, Button, Entry, StringVar, filedialog
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# File Paths
BALANCE_FILE = "balance.json"
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"
HASH_FILE = "balance.hash"

# Generate Recovery Phrases
def generate_recovery_phrase():
    words = [secrets.token_hex(2) for _ in range(12)]  # 12-word recovery phrase
    return " ".join(words)

# Restore Private Key from Recovery Phrase
def restore_private_key_from_phrase(phrase):
    try:
        seed = hashlib.sha256(phrase.encode()).digest()
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=None,
        )
        return private_key
    except Exception as e:
        raise ValueError("Invalid recovery phrase")

# Save Keys to Disk
def save_keys(private_key):
    with open(PRIVATE_KEY_FILE, "wb") as priv_file:
        priv_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    public_key = private_key.public_key()
    with open(PUBLIC_KEY_FILE, "wb") as pub_file:
        pub_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

# Load Balance
def load_balance():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as file:
            balance = json.load(file)
        verify_balance_hash(balance)
        return balance
    return {}

# Save Balance
def save_balance(balance):
    with open(BALANCE_FILE, "w") as file:
        json.dump(balance, file)
    save_balance_hash(balance)

# Save Balance Hash
def save_balance_hash(balance):
    hash_value = hashlib.sha256(json.dumps(balance, sort_keys=True).encode()).hexdigest()
    with open(HASH_FILE, "w") as file:
        file.write(hash_value)

# Verify Balance Integrity
def verify_balance_hash(balance):
    try:
        with open(HASH_FILE, "r") as file:
            stored_hash = file.read()
        current_hash = hashlib.sha256(json.dumps(balance, sort_keys=True).encode()).hexdigest()
        if stored_hash != current_hash:
            raise ValueError("Balance integrity check failed")
    except FileNotFoundError:
        print("No hash file found. Assuming first-time initialization.")

# GUI Functions
def create_wallet():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=None,
    )
    save_keys(private_key)
    recovery_phrase = generate_recovery_phrase()
    wallet_address = hashlib.sha256(recovery_phrase.encode()).hexdigest()

    # Save initial balance
    balance = load_balance()
    balance[wallet_address] = 0
    save_balance(balance)

    result.set(f"Wallet created!\nAddress: {wallet_address}\nRecovery Phrase: {recovery_phrase}\nPlease save your recovery phrase securely.")

def recover_wallet():
    phrase = phrase_entry.get()
    try:
        private_key = restore_private_key_from_phrase(phrase)
        wallet_address = hashlib.sha256(phrase.encode()).hexdigest()
        save_keys(private_key)
        result.set(f"Wallet recovered!\nAddress: {wallet_address}")
    except ValueError as e:
        result.set(f"Failed to recover wallet: {e}")

def check_balance():
    wallet_address = wallet_entry.get()
    balance = load_balance()
    bal = balance.get(wallet_address, "Wallet not found")
    result.set(f"Balance for {wallet_address}: {bal}")

# GUI Setup
root = Tk()
root.title("LMC Wallet")

Label(root, text="LMC Wallet Management", font=("Arial", 16)).pack(pady=10)

frame = StringVar()
phrase_label = Label(root, text="Recovery Phrase:")
phrase_label.pack()
phrase_entry = Entry(root, width=50, textvariable=frame)
phrase_entry.pack()

Button(root, text="Recover Wallet", command=recover_wallet).pack(pady=5)

wallet_label = Label(root, text="Wallet Address:")
wallet_label.pack()
wallet_entry = Entry(root, width=50)
wallet_entry.pack()

Button(root, text="Check Balance", command=check_balance).pack(pady=5)

Button(root, text="Create New Wallet", command=create_wallet).pack(pady=5)

result = StringVar()
result_label = Label(root, textvariable=result, wraplength=400, justify="left")
result_label.pack(pady=10)

root.mainloop()
