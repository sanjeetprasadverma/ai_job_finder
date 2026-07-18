import hashlib

def get_hash(string:str):
    return hashlib.sha256(string.encode()).hexdigest()