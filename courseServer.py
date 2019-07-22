import json
import sys
import signal
import time
import logging

import main
from settingsHandler import SettingsHandler
from TelegramBot import TelegramBot

server = None


class courseServer:

    def __init__(self, settings):
        self.logger = logging.getLogger("courseServer")
        fh = logging.FileHandler("./logs/courseServer.log")
        fh.setFormatter(logging.Formatter(settings.loggingFormat))

        self.logger.addHandler(fh)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False # disable console logger output


        self.data = {}
        self.settings = settings
        self.settings.courseServer = self
        
        global server
        server = self 

    def availableSemeseter(self):
        semAvailable = set()

        for x in self.data:
            semAvailable.add(self.data[x]['Semester'])
        
        #print("Vorhandene Semeseter: " + str(semAvailable))

        return semAvailable


    def saveCourses(self, dataObj):
        print("Saving courses to " + self.settings.filename)
        
        try:
            if not isinstance(dataObj, dict):
                ValueError("saveCourses: dataObj must be a dictonary")
            
            with open(self.settings.filename, "w") as file:
                file.write(self.settings.username + "\n")
                print(json.dumps(dataObj))
                file.write(json.dumps(dataObj))
        except:
            self.logger.exception("saveCoureses():")


    def loadCourses(self):
        self.logger.info("Loading courses from " + self.settings.filename)
        try:
            with open(self.settings.filename, "r") as file:
                data = file.readlines()
                uname = data[0][:-1] # remove \n at the end

            if uname == self.settings.username:
                self.data = json.loads(data[1])
                self.logger.info("Courses loaded")

            else:
                self.logger.warning("Logged in user does not match saved user. " + self.settings.filename + " will be deleted...")
                open(self.settings.filename, "w").close() # delete entrys

        except:
            self.logger.exception("loadCourses():")

    def local_refreshData(self, json_data):
        newData = json.loads(json_data)
        changes = {}

        #{'15000': {'Semester': 'SS 18', 'Name': 'Betriebssysteme', 'Status': 'bestanden'}}

        for modulNr in newData:
            if modulNr in self.data:
                if newData[modulNr]["Status"] == "bestanden" and self.data[modulNr]["Status"] != "bestanden" and "\n" not in newData[modulNr]["Note"]:
                    self.logger.info("Modul '" + newData[modulNr]["Name"] + "' (" + modulNr + ") wurde veröffentlicht.")
                    changes[modulNr] = newData[modulNr]
            else:
                if  "\n" not in newData[modulNr]["Note"]: # to fix a bug when using uberspace, which changes the "Note" to '\n\t\t\t\t..'
                    self.logger.info("Modul '" + newData[modulNr]["Name"] + "' (" + modulNr + ") wurde veröffentlicht.")
                    changes[modulNr] = newData[modulNr]


        if len(changes) > 0 or len(self.data) == 0:
            self.saveCourses(newData)

            self.data = newData
        
        return changes