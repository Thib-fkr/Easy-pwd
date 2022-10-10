# Easy-pwd
A somewhat basic password manager for web application in python.

**As for now, the purpose of this project is to have fun and to learn about cryptography.**

It is not recommended to "[roll your own](https://security.stackexchange.com/questions/18197/why-shouldnt-we-roll-our-own/)" when speaking about cybersecurity tools. Once again, this project is for educationnal purposes only and should not be used in a professional environment. 

## Install
Supposing you have python (>= 3.10.4) and pip installed, you just have to run setup.py as below :

```bash
python src/setup.py
```

Setup.py will perform every tasks by default.
If you know what you are doing, you can make setup.py perform tasks independently by placing as many as you want of the flags that are described below behind a single dash symbol (example follows the description of the flags).

The **d** flag install depedencies listed in [requirements.txt](requirements.txt).

The **p** flag prompt the user to chose a new **storage path**.
Please only use it when you launch the program for the first time in order to chose where your data will be stored, preferably in an external storage device.
*If you change the storage path afterwards, the data previously stored there won't be deleted automaticaly.*

The **m** flag prompt the user to create a master password.
Please also only use it when you launch the program for the first time.
There is no way to change the master password *and* keeping the stored data *yet*.

For running every available tasks :
```bash
python src/setup.py -mdp
```