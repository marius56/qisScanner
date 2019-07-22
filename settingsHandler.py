import logging


loggingFormat = "%(asctime)s %(name)-20s %(levelname)-8s %(message)s"


class SettingsHandler:
    def __init__(self):
        self.local = False # avoid sending over post/get --> without https certificate 
        self.username = ""
        self.password = ""
        self.key = ""
        self.filename = "courses.txt"
        self.botToken = ''
        self.loggedIn = False
        self.relogin = True # Set to false if you dont want to store your password to enable the relogin feature by standard
        self.scanDelay = 60 # amount of seconds to wait between scans

        self.courseServer = None
        self.qisScanner = None
        self.telegramBot = None

        self.loggingFormat = loggingFormat
        self.logger = logging.getLogger("SettingsHandler")
        fh = logging.FileHandler("./logs/settingsHandler.log")
        fh.setFormatter(logging.Formatter(self.loggingFormat))

        self.logger.addHandler(fh)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False # disable console logger output

    def saveSettings(self):
        with open("settings.cfg", "w") as file:
            file.write("relogin=" + str(self.relogin) + "\n")
            file.write("courseFile=" + self.filename + "\n")
            file.write("botToken=" + self.botToken + "\n")
            file.write("scanDelay=" + str(self.scanDelay) + "\n")


    def loadSettings(self):
        try:
            with open("settings.cfg", "r") as file:
                for line in file.readlines():
                    if line.startswith("relogin="):
                        self.relogin = bool(line[len("relogin="):-1])
                    if line.startswith("courseFile="):
                        self.filename = line[len("courseFile="):-1]
                    if line.startswith("botToken="):
                        self.botToken = line[len("botToken="):-1]
                    if line.startswith("scanDelay="):
                        self.scanDelay = int(line[len("scanDelay="):-1])

        except FileNotFoundError:
            self.logger.warning("loadSettings: Settings file not found, creating new one...")
            self.saveSettings()
