from db import BotDB
from steampy.guard import generate_one_time_code

class Main(): #
    def __init__(self):
        self.db = BotDB()

    def executeSDA(self, login: str):
        self.login = login
        accountData = self.db.findAccount(self.login)
        return generate_one_time_code(accountData[6])