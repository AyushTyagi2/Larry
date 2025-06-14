# tasks/security/password.py
import random
import string
import json
import os
import getpass
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PASSWORD_FILE = "passwords.enc"
SALT_FILE = "salt.dat"

def generate_password(length=16, include_uppercase=True, include_digits=True, include_symbols=True):
    """Generate a secure random password"""
    if length < 8:
        print("Password length should be at least 8 characters. Using 8.")
        length = 8
    
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase if include_uppercase else ""
    digits = string.digits if include_digits else ""
    symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?" if include_symbols else ""
    
    # Ensure at least one character from each included set
    all_chars = lowercase + uppercase + digits + symbols
    password = []
    
    # Always include lowercase
    password.append(random.choice(lowercase))
    
    # Include at least one of each enabled type
    if include_uppercase:
        password.append(random.choice(uppercase))
    if include_digits:
        password.append(random.choice(digits))
    if include_symbols:
        password.append(random.choice(symbols))
    
    # Fill the rest randomly
    while len(password) < length:
        password.append(random.choice(all_chars))
    
    # Shuffle the password
    random.shuffle(password)
    final_password = ''.join(password)
    
    print(f"Generated password: {final_password}")
    return final_password

def _get_encryption_key(master_password):
    """Derive encryption key from master password"""
    # Load or create salt
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, "rb") as f:
            salt = f.read()
    else:
        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
    
    # Derive key from password and salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key

def _load_passwords(master_password):
    """Load and decrypt stored passwords"""
    if not os.path.exists(PASSWORD_FILE):
        return {}
    
    try:
        key = _get_encryption_key(master_password)
        fernet = Fernet(key)
        
        with open(PASSWORD_FILE, "rb") as f:
            encrypted_data = f.read()
        
        decrypted_data = fernet.decrypt(encrypted_data)
        passwords = json.loads(decrypted_data.decode())
        return passwords
    except Exception as e:
        print(f"Error decrypting passwords. Wrong master password or corrupted file: {e}")
        return None

def _save_passwords(passwords, master_password):
    """Encrypt and save passwords"""
    try:
        key = _get_encryption_key(master_password)
        fernet = Fernet(key)
        
        encrypted_data = fernet.encrypt(json.dumps(passwords).encode())
        
        with open(PASSWORD_FILE, "wb") as f:
            f.write(encrypted_data)
        
        return True
    except Exception as e:
        print(f"Error saving passwords: {e}")
        return False

def add_password(master_password, service, username, password=None):
    """Add or update a password entry"""
    passwords = _load_passwords(master_password)
    
    if passwords is None:
        return False
    
    # Generate password if not provided
    if password is None:
        length = int(input("Password length (default: 16): ") or 16)
        use_uppercase = input("Include uppercase letters? (y/n, default: y): ").lower() != 'n'
        use_digits = input("Include digits? (y/n, default: y): ").lower() != 'n'
        use_symbols = input("Include symbols? (y/n, default: y): ").lower() != 'n'
        
        password = generate_password(length, use_uppercase, use_digits, use_symbols)
    
    # Save the password
    if service not in passwords:
        passwords[service] = {}
    
    passwords[service][username] = password
    success = _save_passwords(passwords, master_password)
    
    if success:
        print(f"Password for {service} ({username}) saved successfully!")
    
    return success

def get_password(master_password, service=None):
    """Retrieve stored passwords"""
    passwords = _load_passwords(master_password)
    
    if passwords is None:
        return False
    
    if not passwords:
        print("No passwords stored yet.")
        return False
    
    if service is None:
        # List all services
        print("\nStored services:")
        for i, s in enumerate(sorted(passwords.keys()), 1):
            print(f"{i}. {s}")
        
        try:
            choice = int(input("\nSelect a service number (0 to cancel): "))
            if choice == 0:
                return False
            
            service = sorted(passwords.keys())[choice-1]
        except (ValueError, IndexError):
            print("Invalid selection")
            return False
    
    if service in passwords:
        if len(passwords[service]) == 1:
            username = list(passwords[service].keys())[0]
            password = passwords[service][username]
            print(f"\nService: {service}")
            print(f"Username: {username}")
            print(f"Password: {password}")
        else:
            print(f"\nUsernames for {service}:")
            usernames = list(passwords[service].keys())
            for i, username in enumerate(usernames, 1):
                print(f"{i}. {username}")
            
            try:
                choice = int(input("\nSelect a username number: "))
                username = usernames[choice-1]
                password = passwords[service][username]
                print(f"\nService: {service}")
                print(f"Username: {username}")
                print(f"Password: {password}")
            except (ValueError, IndexError):
                print("Invalid selection")
                return False
        
        return True
    else:
        print(f"No passwords found for {service}")
        return False

def initialize_password_manager():
    """Set up the password manager with a master password"""
    if os.path.exists(PASSWORD_FILE):
        print("Password manager already initialized.")
        return True
    
    print("\n=== Password Manager Setup ===")
    print("Create a master password to secure your passwords.")
    print("WARNING: If you forget this password, you cannot recover your stored passwords!")
    
    while True:
        master_password = getpass.getpass("Create master password: ")
        if len(master_password) < 8:
            print("Master password must be at least 8 characters long")
            continue
        
        confirm = getpass.getpass("Confirm master password: ")
        if master_password != confirm:
            print("Passwords don't match! Try again.")
            continue
        
        break
    
    # Initialize empty password vault
    success = _save_passwords({}, master_password)
    
    if success:
        print("Password manager initialized successfully!")
    else:
        print("Failed to initialize password manager.")
    
    return success