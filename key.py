import secrets

# Generate a 32-byte secure random key
secret_key = secrets.token_hex(32)
print(secret_key)
