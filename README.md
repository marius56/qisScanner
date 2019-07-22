# qisScanner

## Prerequisites 
---
You need to install the following modules to make the programm work

    pip3 install cryptography # Encrypte the password for the relogin feature

    pip3 install python-telegram-bot # The API to control the Telegram bot

    pip3 install requests # To send requests to the qis websites

---

## Setup
1. Insert your Telegram chat ID into the *chatIDs.cfg* file
2. Execute: 
    >python3 main.py
3. Enter your username, password and bot token.


---
## Settings
You can change the delay between the qis checks aswell as the relogin feature in the *settings.cfg* file.

If the *relogin* feature is enabled (True) the programm encrypts the entered password with a random key and stores it in the settings.password variable. This way it isnt visible in clear text in the ram. If an error occurs, the programm trys to login again using the stored password and username.