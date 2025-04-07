from cryptography.fernet import Fernet

def generate_key():
    # Genera una nuova chiave segreta per Fernet
    key = Fernet.generate_key()

    # Salva la chiave in un file
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

    print("Chiave generata e salvata come 'secret.key'")

if __name__ == "__main__":
    generate_key()