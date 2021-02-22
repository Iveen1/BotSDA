from pywinauto import application
from pywinauto import clipboard
import time
import parserJSON
from db import BotDB

class Main(): #
    def __init__(self):
        self.db = BotDB()

    def executeSDA(self, login: str):
        self.login = login
        accountData = self.db.findAccount(self.login)
        if accountData != None:
            parserJSON.parser(accountData[3])

            app = application.Application()
            app.start(r'SDA\Steam Desktop Authenticator.exe', timeout=5)
            sda = app.window(title_re="Steam Desktop Authenticator")
            time.sleep(2)
            sda.Copy.click()
            code = clipboard.GetData()
            sda.close()
            return code
        else:
            return