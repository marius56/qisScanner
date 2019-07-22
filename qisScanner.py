import requests
import json
import time
import sys
import os
import logging
from cryptography.fernet import Fernet

from qisHTMLParser import qisHTMLParser

class qisScanner:
    s = requests.session()
    parser = qisHTMLParser()

    def __init__(self, mainPid, settings):
        self.courseHTML = ""
        self.mainPid = mainPid
        self.settings = settings
        self.settings.qisScanner = self

        self.logger = logging.getLogger("qisScanner")
        fh = logging.FileHandler("./logs/qisScanner.log")
        fh.setFormatter(logging.Formatter(settings.loggingFormat))

        self.logger.addHandler(fh)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False # disable console logger output. Set to True if you want to see the logs in the console


    def login(self):
        f = Fernet(self.settings.key)

        payload = {'asdf': self.settings.username, 'fdsa': f.decrypt(self.settings.password).decode() }
        
        try:
            result = self.s.post('https://qis.hs-albsig.de/qisserver/rds;?state=user&type=1&category=auth.login&re=last&startpage=portal.vm', params=payload)
            if "Sie sind angemeldet als:" in result.text:
                #print("angemldet")
                self.logger.info("Login successful")
                return True

            #print("Falscher benutzername/password")
            return False

        except:
            self.logger.exception("login():")
            return False

    def fetchCourses(self):
        self.logger.info("Fetching courses...")

        try:
            r = self.s.get('https://qis.hs-albsig.de/qisserver/rds?state=change&type=1&moduleParameter=studyPOSMenu&nextdir=change&next=menu.vm&subdir=applications&xml=menu&purge=y&navigationPosition=functions%2CstudyPOSMenu&breadcrumb=studyPOSMenu&topitem=functions&subitem=studyPOSMenu')

            content = str(r.content.decode("utf-8"))

            if "Benutzerkennung" in content: # Session broke 
                return False

            asiPos = content.find('asi')
            asi = content[asiPos+4:asiPos+24]
            #print("AsiToken: " + asi)
        except:
            self.logger.exception("fetchCoures(): Getting ASI number")

        try:
            self.courseHTML = self.s.get('https://qis.hs-albsig.de/qisserver/rds?state=notenspiegelStudent&next=list.vm&nextdir=qispos/notenspiegel/student&createInfos=Y&struct=auswahlBaum&nodeID=auswahlBaum%7Cabschluss%3Aabschl%3D84%2Cstgnr%3D1&expand=0&asi=' + asi + '#auswahlBaum%7Cabschluss%3Aabschl%3D84%2Cstgnr%3D1').text
            
            if "ECTS-Gesamtkonto" not in self.courseHTML: # if the session is broken, the response will not contain "ECTS-Gesamtkonto" 
                return False
            
            return True
        
        except:
            self.logger.exception("fetchCourses():")

    def parseCourses(self):
        self.logger.info("Parsing data...")
        self.parser.feed(self.courseHTML)

    def getCourses(self):
        return self.parser.getCourses()
    
    def createJson(self):
        data = {}

        for course in self.getCourses():
            nr = str(course.modulnr)
            data[nr] = {}
            data[nr]["Name"] = course.name
            data[nr]["Semester"] = course.sem
            if course.grade:
                data[nr]["Note"] = course.grade
            if course.status:
                data[nr]["Status"] = course.status
            if course.ects:
                data[nr]["ECTS"] = course.ects
            if course.ects:
                data[nr]["pArt"] = course.pArt
            if course.date:
                data[nr]["Datum"] = course.date

        return json.dumps(data)
    
    def local_sendJsonData(self, json_data):
        self.logger.info("Updating course data(locally)...")     

        courses = self.settings.courseServer.local_refreshData(json_data)

        return courses


    def sendJsonData(self, json_data):
        self.logger.info("Updating course data...")     
        result = requests.post(self.settings.url + ":" + str(self.settings.port) + "/newData", data=json_data)

        courses = json.loads(result.text) 
        """if len(courses) :
            print("Es wurden Prüfungsergebnise veröffentlicht:")
            for mNr in courses:
                print(courses[mNr]["Name"] + "(" + mNr + "): " + courses[mNr]["Status"])
        """
        return courses
                



    def logout(self):
        self.s.get('https://qis.hs-albsig.de/qisserver/rds?state=user&type=4&re=last&category=auth.logout&breadCrumbSource=portal&topitem=functions')




    scanner = None

    def start(self):

        self.scanner = self
        #self.scanner.login()

        running = True
        try:
            while (running):
                self.scanner.fetchCourses()
                self.scanner.parseCourses()

                json_data = self.scanner.createJson()
                self.scanner.sendJsonData(json_data)
                """s.sendJsonData(\"""
                {
                    "16500": {      
                        "Status": "bestanden",
                        "ECTS": "0,0",
                        "Name": "Formale Grundlagen",
                        "Semester": "SS 18"
                    }
                }\""")""" 

                print()
                time.sleep(5)
                

            for x in s.getCourses():
                #print("'" + str(x.grade + "'")
                #print(ord(x.grade[0]))
                print(x)
        except:
            pass


