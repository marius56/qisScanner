import signal
import sys
import time
import os
import logging
import getpass
from cryptography.fernet import Fernet

import courseServer
import qisScanner 
from TelegramBot import TelegramBot
from settingsHandler import SettingsHandler
import settingsHandler


def login():
    success = settings.qisScanner.login()
    
    if success == True:
        settings.courseServer.loadCourses()
        settings.loggedIn = True

    return success

def logout():
    logger.info("Logging out from qis...")
    settings.qisScanner.logout()
    settings.loggedIn = False

if __name__ == "__main__":

    print("\n\n##########| QIS Scanner started |##########")
    print("Press Ctrl+C to exit the programm\n")

    
    if not os.path.exists("./logs"):
        os.mkdir("./logs")
        print("Creating logs folder...")

    #logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='main.log')
    logging.basicConfig(level=logging.INFO,format=settingsHandler.loggingFormat,datefmt='%Y-%m-%d %H:%M:%S',)
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARNING) # removes the: requests.packages.urllib3.connectionpool INFO     Resetting dropped connection: qis.hs-albsig.de
    logger = logging.getLogger("main")
    fh = logging.FileHandler("./logs/main.log")
    fh.setFormatter(logging.Formatter(settingsHandler.loggingFormat))
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False # disable console logger output

    logger.info("Logger started...")

    settings = SettingsHandler()
    courseServer.courseServer(settings)

    qisScanner.qisScanner(os.getpid(), settings)

    try:
        logger.info("Loading settings...")
        print("Loading settings...")
        settings.loadSettings()
      

        logger.info("Starting Telegram Bot...")
        print("Starting Telegram Bot...")
        telegramBot = TelegramBot(settings)

        if telegramBot.setupBot(settings.botToken) == False:
            print("No valid Bot Token available. Please insert a valid one:")
            logger.error("No valid Bot Token available.")

            while telegramBot.setupBot(input("Bot Token: ")) == False:
                print("\nUnvalid bot token. Please try again...")

            logger.info("Valid bot token entered.")
            print("Bot token valid! Telegram bot connected")
            settings.saveSettings()


        print("\nPlease log into your qis account: ")
        
        settings.key = Fernet.generate_key()
        f = Fernet(settings.key)

        while True:
            settings.username = input("Name: ")
            settings.password = f.encrypt(getpass.getpass(prompt='Password:', stream=None).encode()) # to not store password in clear text
            login()
            
            if settings.loggedIn:
                break
            
            print("\nWrong data! Try again:")
            

        settings.relogin = True # Set to False if you dont want to save the password and relogin

        if settings.relogin == False:
            settings.password = "0" * len(settings.password) # clear the password



        
        

        errorMessageSent = False
        print("\nStarting to scan qis for new courses (every " + str(settings.scanDelay) + "sec)")

        while (True):
            if settings.qisScanner.fetchCourses() == False:

                if errorMessageSent == False:
                    settings.qisScanner.logout()
                    settings.loggedIn = False

                    if settings.relogin == True:
                        logger.error("Access to server not possible. Trying to relogin.")
                        telegramBot.sendMessage("Info: Access to server not possible...\nTrying to relogin.")
                    else:
                        logger.error("Access to server not possible.")
                        telegramBot.sendMessage("Info: Access to server not possible...\nPlease try to login again.")

                    errorMessageSent = True
                    if login() == False:
                        logger.error("Unable to relogin.")
                        telegramBot.sendMessage("Info: Unable to relogin, retrying every 60sec.")

                time.sleep(60)
                login()
                continue

            if errorMessageSent == True:
                errorMessageSent = False
                telegramBot.sendMessage("Info: Access to server restored!")
                logger.info("Access to server restored")

            settings.qisScanner.parseCourses()
            
            json_data = settings.qisScanner.createJson()
            newCourses = {}

            newCourses = settings.qisScanner.local_sendJsonData(json_data)
            
            if newCourses != None and len(newCourses):
                text = "There are new exam results available:\n"

                for mNr in newCourses:
                    if "Note" in newCourses[mNr]: #newCourses[mNr]["pArt"] == "MP": # Remove the duplications and only displays the modul exams
                        text += newCourses[mNr]["Name"] + ": " + newCourses[mNr]["Note"] + '\n'
                        logger.info("New coures: %s - Status: %s - Grade: %s"% (newCourses[mNr]["Name"], newCourses[mNr]["Status"], newCourses[mNr]["Note"]))

                telegramBot.sendMessage(text)
            time.sleep(settings.scanDelay)

    except KeyboardInterrupt:
        print("\n\n\nCtrl-C pressed. Stopping programm...\n")
        
        if settings.loggedIn == True:
            print("[Info]: Logging out from qis...")
            logout()

                
        logger.info("Saving settings...")
        print("[Info]: Saving settings...")
        settings.saveSettings()

        try:
            if settings.telegramBot.updater.dispatcher.running == True:
                logger.info("Stopping telegram bot...")
                print("[Info]: Stopping telegram bot...")
                settings.telegramBot.stop()
        except: # if the telegram bot was not started yet, it throws an exception
            pass

        logger.info("Exiting programm...")
        print("Exiting programm...")

    except:
        logger.exception("main:")