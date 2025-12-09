from cryptography.fernet import Fernet
import os

key = os.environ["IPE_SECRET_ENC_KEY"]  # 32-byte base64 string
fernet = Fernet(key)

def encrypt_secret(value: str) -> bytes:
    return fernet.encrypt(value.encode("utf-8"))

def decrypt_secret(blob: bytes) -> str:
    return fernet.decrypt(blob).decode("utf-8")
