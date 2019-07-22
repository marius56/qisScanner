from telegram import Bot
from telegram.ext import Updater, CommandHandler
from telegram.error import InvalidToken

import logging
import sys

tBot = None

class TelegramBot:
    def __init__(self, settings): #, chatID, botToken):
        self.logger = logging.getLogger("TelegramBot")
        fh = logging.FileHandler("logs/TelegramBot.log")
        fh.setFormatter(logging.Formatter(settings.loggingFormat))
        self.logger.addHandler(fh)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False # disable console logger output

        self.settings = settings
        self.settings.telegramBot = self
        self.bot = None
        self.updater = None
        self.chatIDs = []
        self.loadChatIDs()


        global tBot
        tBot = self

    def setupBot(self, token):
        try:
            self.bot = Bot(token)
            self.updater = Updater(token)
        except InvalidToken:
            self.logger.critical("setupBot: Invalid Bot Token")
            return False

        try:
            dp = self.updater.dispatcher
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(CommandHandler("subscribe", subscribe))
            dp.add_handler(CommandHandler("unsubscribe", unsubscribe))
            dp.add_handler(CommandHandler("ects", ects))
            dp.add_handler(CommandHandler("bestanden", bestanden))
            dp.add_handler(CommandHandler("average", average))
            
            dp.add_error_handler(error)
            self.updater.start_polling()
            #self.updater.idle()
            
            self.settings.botToken = token

            return True

        except:
            self.logger.exception("setupBot:")
            

    def sendMessage(self, text):
        for chatID in self.chatIDs:
            self.bot.send_message(chat_id=chatID, text=text)   

    def saveChatIDs(self):
        with open("chatIDs.cfg", "w") as file:
            for chatID in self.chatIDs:
                file.write(str(chatID) + "\n")
            
    def loadChatIDs(self):
        try:
            with open("chatIDs.cfg", "r") as file:
                for line in file.readlines():
                    self.chatIDs.append(int(line))

            self.logger.info("%d Telegram chatID(s) loaded."% (len(self.chatIDs)))
        except FileNotFoundError:
            self.logger.warning("loadChatIDs: chatIDs.cfg not found. Creating new file...")
            print("[Info]: No chatIDs found.. insert your chatID into the chatIDs.cfg file.")
            open("chatIDs.cfg", "w").close()
    
    def stop(self):
        self.updater.dispatcher.stop()
        self.updater.stop()

    @staticmethod
    def start(bot, update, chatIDs):
        #print("Test: " + str(update.message.chat_id))
        update.message.reply_text('Test!')
        bot.send_message(chat_id=chatIDs[0], text="Test")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    tBot.logger.error('Update: "%s" caused error "%s"'% (update, error))

def start(bot, update):
        update.message.reply_text("""HS Albsig qis Bot - Overview\n
/subscribe\nGet informed about new result releases\n
/unsubscribe\nStop the service\n
/ects\nGet the sum of your ECTS points\n
/bestanden\nShows the passed exams\n
/average:\nShows your avaerage grade""")


def ects(bot, update):
    points = 0.0

    for course in tBot.settings.courseServer.data:
        try:
            points += float(tBot.settings.courseServer.data[course]["ECTS"].replace(",", "."))
        except:
            pass
            
    print(points)
    update.message.reply_text("Your current ECTS sum: " + str(points))

def average(bot, update):
    grade = 0.0
    counter = 0

    for course in tBot.settings.courseServer.data:
        try:
            grade += float(tBot.settings.courseServer.data[course]["Note"].replace(",", "."))
            counter = counter + 1
        except:
            pass
            
    update.message.reply_text("Your current average grade is: " + str(round(grade/counter, 2)))


def bestanden(bot, update):
    text = "Passed exams:\n"
    for course in tBot.settings.courseServer.data:

        if tBot.settings.courseServer.data[course]["Status"] == "bestanden" and "Note" in tBot.settings.courseServer.data[course] and "\n" not in tBot.settings.courseServer.data[course]["Note"]: # tBot.settings.courseServer.data[course]["pArt"] == "MP":
            text += "- " + tBot.settings.courseServer.data[course]["Name"]
            try:
                if "Note" in tBot.settings.courseServer.data[course]:
                    text += " (" + tBot.settings.courseServer.data[course]["Note"] + ")"
            except:
                e = sys.exc_info()[0]
                tBot.logger.error("bestanden: " + str(e))
            
            text += "\n"

    update.message.reply_text(text)



def subscribe(bot, update):
    if update.message.chat_id in tBot.chatIDs:
        update.message.reply_text("Your are already registered.\nYou can use /unsubscribe to stop my service for you.")
        return

    tBot.chatIDs.append(update.message.chat_id)
    update.message.reply_text("Your subscribtion was successfull.\nI will inform you if new results are available.\nYou can use /unsubscribe to stop my service for you.")
    tBot.saveChatIDs()

    tBot.logger.info("New Chat (%s) registered."% (str(update.message.chat_id)))


def unsubscribe(bot, update):
    if update.message.chat_id not in tBot.chatIDs:
        update.message.reply_text("Your are not registered.\nYou can use /subscribe if you wish to be informed about new results.")
        return

    tBot.chatIDs.remove(update.message.chat_id)
    tBot.saveChatIDs()
    update.message.reply_text("Your successfully unsubscribed from my list.\nYou can use /subscribe if you wish to be informed about new results.")

    tBot.logger.info("Chat (%s) unsubscribed."% (str(update.message.chat_id)))
