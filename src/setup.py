    
from sys import executable, argv
from subprocess import CalledProcessError, check_call
from socket import gethostbyname, gethostname
from os.path import exists

def main():
    
    # Verifying command line argument
    
    # Check number of arguments
    if (len(argv) == 2):
        arg = argv[1]
        
        # Check argument format
        if arg[0] == '-':
            # Is it asked to install dependencies ?
            if 'd' in arg:
                if install_dependencies() == 1:
                    return
            
            # Is it asked to change storage path ?
            if 'p' in arg:
                if change_storage_path() == 1:
                    return
            
            # Quit the program if all selected tasks have been performed
            return

        else:
            print("[-] Wrong argument format, please read the manual for more informations on supported arguments")

    elif (len(argv) != 1):
        print(f"[-] Excepted 0 or 1 argument, {len(argv)-1} received")
        return
    
    # If no argument has been detected, try to perform every task
    else:
        if install_dependencies() == 1:
            return
        
        if change_storage_path() == 1:
            return
  
          
def install_dependencies() -> int:
    """
    First check the internet connectivity, then try to install dependencies from requirements.txt
    
    Output :
    --------
    0 : if it encounters an error
    1 : Otherwise
    """
    # Check internet connection
    address = gethostbyname(gethostname())
    if address == "127.0.0.1":
        print("[-] Please connect your device to the internet, then try to re-try")
        return 1

    print("[+] Connected to internet !")
    
    
    # Install dependencies
    print("[+] Installing requirements...")
    try:
        check_call([executable, '-m', 'pip', 'install', '-r','requirements.txt'])
    except CalledProcessError as e:
        print("[-] Something when wrong when installing dependencies")
        print(f"[-] Error code -> {e.returncode}")
        return 1
    
    return 0


def change_storage_path() -> int:
    """
    Prompt the user to input a new path for storage.
    
    Output :
    --------
    0 : if it encounters an error
    1 : Otherwise
    """
    # Prompting user to enter storage path
    while True:
        path = input("Enter the path of the storage device you want to put the data into : ")
        
        # If the path is valid
        if exists(path):
            try:
                from yaml import Loader, Dumper, load, dump
            except ImportError as e:
                print("[-] Something went wrong while importing modules")
                print("[-] Please install needed dependencies with the flag -d")
                return 1

            # Load config data
            with open("data/config.yml", "r") as f:
                data = load(f, Loader=Loader)
                if (data is None) or (len(data) == 0):
                    print["[-] Something went wrong while reading config.yml"]
                    return 1
                data["path"] = path

            # Write updated config data
            with open("data/config.yml", "w") as f:
                dump(data, f, Dumper=Dumper)

            break
        else:
            print("[-] Invalid path name")
    
    return 0
            

if __name__ == "__main__":
    main()