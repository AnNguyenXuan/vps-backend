from cryptography.fernet import Fernet
from app.core import config

cipher = Fernet(config.FERNET_KEY.encode())

def encrypt(text: str) -> str:
    return cipher.encrypt(text.encode()).decode()

def decrypt(cipher_text: str) -> str:
    return cipher.decrypt(cipher_text.encode()).decode()
