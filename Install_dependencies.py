import os

def install_dependencies():
    os.system("pip install requests pillow scipy cryptography pynput sounddevice pywin32")
    print("Tutte le dipendenze sono state installate correttamente.")

if __name__ == "__main__":
    install_dependencies()