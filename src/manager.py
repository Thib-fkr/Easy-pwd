from os import urandom
from os.path import isfile
from re import fullmatch
from unicodedata import normalize

from yaml import dump, Dumper, load, Loader
from getpass import getpass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def create_master_pwd():
    """
    Prompt the user to create a master password.
    """
    # Verify if a verification file is already present
    if isfile("data/verification.yml"):
        print("[-] Master password already created.")
        return
    
    # Display a text to help the user chose his password
    print("[+] In order to use the application, you need to chose a password")
    print("[+] You will be asked to type it whenever you want to launch the application\n")
    print("[+] It is important to chose a strong password (at the very least 16 characters), with :")
    print("\t-lowercase and uppercase letters\n\t-digits\n\t-special characters\n")
    

    # Password requirements
    # ---------------------
    #   condition                     : regex expression
    #
    #   at least one uppercase letter : (?=.*?[A-Z])
    #   at least one lowercase letter : (?=.*?[a-z])
    #   at least one digit            : (?=.*?[0-9])
    #   at least one special charcater: (?=.*?[\s-._!\"`'#%&,:;<>=@{}~\$\(\)\*\+\/\\\?\[\]\^\|])
    #   at least 16 characters        : {16,}
    #
    pattern = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[\s\-._!\"`'#%&,:;<>=@{}~\$\(\)\*\+\/\\\?\[\]\^\|]).{16,}$"

    while True:
        # Get password
        pwd = getpass("[+] Enter your password :")
        # Verify password strength
        if fullmatch(pattern, pwd):
            if getpass("[+] Enter your password again to confirm :") == pwd:
                pwd = normalize("NFKD", pwd)
                break
            else:
                print("[-] Your passwords do not match, please try again")
        else:
            print("[-] Entered password does not match the above condition, please try again")

    # Prepare the salt for the KDF
    salt1 = urandom(32)
    
    # Create Key Derivation Function using PBKDF2-HMAC-SHA256 with 123 456 iterations
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt1,
        iterations=123456,
        )
    
    # Here is the encryption key for AES encryption
    pwd = kdf.derive(pwd.encode())
    
    # Generate encryption algorithm : AES-256-GCM
    enc = AESGCM(pwd)
    
    # Prepare the salt
    salt2 = urandom(32)
    
    # Encrypt the key present in the config file
    with open("data/config.yml", "r") as f:
        encrypted = enc.encrypt(salt2, load(f, Loader=Loader)["key"], None)
    
    data = {
        "algorithm1" : "PBKDF2-HMAC-SHA256(123456)",
        "salt1" : salt1,
        "iterations" : 123456,
        "algorithm2" : "AES-256-GCM",
        "salt2" : salt2,
        "hash" : encrypted
    }

    # Write verification key with encryption information
    with open("data/verification.yml", 'w') as f:
        dump(data, f, Dumper=Dumper)

def verify_master_password() -> bool:
    """
    Return True if the password entered by the user is the master password.
    """
    
    # Get verification key and ecryption information from verification.yml
    with open("data/verification.yml", 'rb') as f:
        data = load(f, Loader=Loader)
    
    # Re-create the KDF
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=data["salt1"],
        iterations=data["iterations"]
    )

    # Re-create encryption algorithm
    enc2 = AESGCM(kdf.derive(getpass().encode()))
    
    # Load the verification key
    with open("data/config.yml", "r") as f:
        key = load(f, Loader=Loader)["key"]
        
    # Compare the verification key with the decrypted data
    return enc2.decrypt(data["salt2"], data["hash"], None) == key
            