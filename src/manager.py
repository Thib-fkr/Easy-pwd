from os import urandom
from os.path import isfile
from re import fullmatch
from unicodedata import normalize

from yaml import dump, Dumper, load, Loader
from getpass import getpass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class Manager():


    def __init__(self):
        self.kek : bytes = b''


    @staticmethod
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


    def register(self):
        """
        Derive the key encryption key from the master password.
        (Might investigate memory safety later)
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
        pwd = kdf.derive(getpass("[+] Enter the master password : ").encode())
        enc2 = AESGCM(pwd)

        # Load the verification key
        with open("data/config.yml", "r") as f:
            key = load(f, Loader=Loader)["key"]

        # Compare the verification key with the decrypted data
        self.kek = pwd if enc2.decrypt(data["salt2"], data["hash"], None) == key else b''


    def register_account(self, site:str, tag1:str, tag2:str):
        """
        Encrypt the authentication information about a website.

        Inputs:
        -------
        site : url of a web page
        tag1 : name of the username field element in HTML page
        tag2 : name of the password field element in HTML page

        Might need to sanitize inputs before manipulating data.
        """

        # Check master password
        key : bytes = self.kek
        if key == b'':
            self.register()
            key = self.kek

        # Get Website list
        with open("data/sites/0.yml", "r") as f:
            data = load(f, Loader=Loader)

        # Get the title of the to-be-created file
        number = next(iter(data["website"][-1].keys())) + 1

        # Append authentication information to website list
        data["website"].append( {number : self.encrypt(key, site.encode())} )

        # Write actualized data to the file
        with open("data/sites/0.yml", "w") as f:
            dump(data, f, Dumper=Dumper)

        # Get authentication information
        username : bytes = input(f"[+] Enter username/email for {site} : ").encode()
        pwd : bytes = getpass(f"[+] Enter password for {site} : ").encode()

        # Encrypt it
        enc_1 = self.encrypt(key, username)
        enc_2 = self.encrypt(key, pwd)

        # Write it in the file
        with open(f"data/sites/{number}.yml", 'w') as f:
            dump({  "algorithm" : enc_1["algorithm"],
                    "salt1" : enc_1["salt"],
                    "username" : enc_1["hash"],
                    "username_tag" : tag1,
                    "salt2" : enc_2["salt"],
                    "password" : enc_2["hash"],
                    "password_tag" : tag2}, f, Dumper=Dumper)


    @staticmethod
    def encrypt(key:bytes, value:bytes, length:int = 32) -> dict:
        """
        Encrypt the value with the key using AES-GCM algorithm.
        """
        # Set default key length to 32 if entered length is not valid
        if length not in (16, 24, 32):
            length = 32

        # Encrypt value
        enc = AESGCM(key)
        salt = urandom(length)
        return {
            "algorithm" : f"AES-{str(length*8)}-GCM",
            "salt" : salt,
            "hash" : enc.encrypt(salt, value, None)
        }


    def decrypt(self, hash:bytes, salt:bytes) -> str:
        """
        Decrypt the value encrypted with AES-GCM algorithm
        """

        pwd = self.kek
        if pwd == b'':
            self.register()
            pwd = self.kek

        enc = AESGCM(pwd)
        return enc.decrypt(salt, hash, None)