import hashlib
import base64
from Crypto.Cipher import AES

def get_user_encryption_key(user_id):
    """
    Generates a unique encryption key for each user.
    """
    return hashlib.sha256(user_id.encode()).digest()

def encrypt_user_data(user_id, data):
    """
    Encrypts sensitive user data using a per-user key.
    """
    key = get_user_encryption_key(user_id)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

def decrypt_user_data(user_id, encrypted_data):
    """
    Decrypts the encrypted data using the user's unique key.
    """
    key = get_user_encryption_key(user_id)
    raw_data = base64.b64decode(encrypted_data)
    nonce, tag, ciphertext = raw_data[:16], raw_data[16:32], raw_data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()
