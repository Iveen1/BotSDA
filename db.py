import sqlite3
import steamPageParser
import os

class BotDB():
    def __init__(self):
        self.db = sqlite3.connect('server.db')
        self.sql = self.db.cursor()


    def showUsers(self):
        self.sql.execute("SELECT * FROM users")
        return self.sql.fetchall()


    def checkUser(self, login: int, reg = False):
        self.sql.execute(f"SELECT login FROM users WHERE login = '{login}'")
        self.user = self.sql.fetchone()

        if self.user is None and reg == True:
            self.newUser(login)
            return

        elif self.user != None and reg == False:
            self.sql.execute(f"SELECT id FROM users WHERE login = '{login}'")
            return self.sql.fetchone()

        else:
            return None


    def newUser(self, login: int):
        self.sql.execute(f"INSERT INTO users ('login') VALUES ('{login}')")
        self.db.commit()
        return f'New user: {login}'


    def checkSDA(self, login: int):
        self.user = self.checkUser(login)
        if self.user != None:
            self.sql.execute(f"SELECT id FROM sda WHERE fk_userId = '{self.user[0]}'")
            self.sdaUser = self.sql.fetchone()

            if self.sdaUser != None:
                return True
        return False

    def addsda(self, login):
        if self.checkUser(login) != None:
            self.sql.execute(f"SELECT id FROM users WHERE login = '{login}'")
            self.foreignKey = self.sql.fetchone()[0]

            self.sql.execute(f"SELECT id FROM sda WHERE fk_userId = '{self.foreignKey}'")
            self.check = self.sql.fetchone()
            if self.check == None:
                self.sql.execute(f"INSERT INTO sda ('fk_userId') VALUES ('{self.foreignKey}')")
                self.db.commit()
                return True
            else: return 'Already'
        else: return False


    def remsda(self, login):
        if self.checkUser(login) != None:
            self.sql.execute(f"SELECT id FROM users WHERE login = '{login}'")
            self.foreignKey = self.sql.fetchone()[0]

            self.sql.execute(f"SELECT id FROM sda WHERE fk_userId = '{self.foreignKey}'")
            self.check = self.sql.fetchone()
            if self.check != None:
                self.sql.execute(f"DELETE FROM sda WHERE fk_userId = '{self.foreignKey}'")
                self.db.commit()
                return True
            else: return 'Already'
        else: return False


    def showsdausers(self):
        self.sql.execute(f"SELECT * FROM sda")
        return self.sql.fetchall()


    def SDAusers(self):
        self.sql.execute(f"SELECT * FROM sda")
        self.out = self.sql.fetchall()
        return self.out


    def findAccount(self, login: str):
        self.sql.execute(f"SELECT * FROM accounts WHERE login = '{login}'")
        return self.sql.fetchone()


    def insertData(self, tablename: str, login: str, columnName: str, data: str):
        self.sql.execute(f"UPDATE {tablename} SET ('{columnName}') = ('{data}') WHERE login = '{login}'")
        self.db.commit()


    def findUserById(self, id: int):
        self.sql.execute(f"SELECT login FROM users WHERE id = '{id}'")
        return self.sql.fetchone()


    def getToken(self):
        self.sql.execute(f"SELECT * FROM token")
        return self.sql.fetchone()[1]


    def subscribers(self):
        self.sql.execute(f"SELECT fk_userId FROM subscribers")
        self.subsId = self.sql.fetchall()
        self.subsLogin = []
        for i in range(len(self.subsId)):
            self.sql.execute(f"SELECT login FROM users WHERE id = '{self.subsId[i][0]}'")
            self.subsLogin.append(self.sql.fetchone())
        return self.subsLogin

class SubsDB():
    def __init__(self):
        self.db = sqlite3.connect('subscriptions.db')
        self.sql = self.db.cursor()


    def receiveItemIds(self):
        self.sql.execute(f"SELECT itemId FROM allLinks")
        a = self.sql.fetchall()
        return a


    def receiveItemUrls(self):
        self.sql.execute(f"SELECT itemLink FROM allLinks")
        a = self.sql.fetchall()
        return a


    def insertData(self, tablename: str, itemId: str, columnName: str, data: str):
        self.sql.execute(f"UPDATE {tablename} SET ('{columnName}') = ('{data}') WHERE itemId = '{itemId}'")
        self.db.commit()


    def receiveUsers(self):
        a = self.receiveItemIds()
        self.ids = []
        for i in range(len(a)):
            self.sql.execute(f"SELECT fk_subscriberId FROM subscribers WHERE fk_allLinks_itemId = {a[i][0]}")
            self.dict = [a[i], self.sql.fetchall()]
            self.ids.append(self.dict)
        return self.ids


    def receiveUsersById(self, userId):
        self.sql.execute(f"SELECT fk_allLinks_itemId FROM subscribers WHERE fk_subscriberId = '{userId}'")
        return self.sql.fetchall()


    def getUrl(self, itemId):
        self.sql.execute(f"SELECT itemLink FROM allLinks WHERE itemId = '{itemId}'")
        self.url = self.sql.fetchone()
        if self.url != None: return self.url[0]
        else: return


    def getItemName(self, itemId):
        self.sql.execute(f"SELECT itemName FROM allLinks WHERE itemId = '{itemId}'")
        self.url = self.sql.fetchone()
        if self.url != None: return self.url[0]
        else: return


    def subscribe(self, login: int, arg):
        self.userId = BotDB().checkUser(login)
        self.itemId = steamPageParser.itemId(arg)
        self.itemName = steamPageParser.itemName(arg)
        if self.itemId == 'Error' or self.itemName == 'Error':
            return "Wrong usage"
        if self.userId != None:
            self.sql.execute(f"SELECT itemId FROM allLinks WHERE itemId = '{self.itemId}'")
            check = self.sql.fetchone()
            if check == None:
                self.sql.execute(f"INSERT INTO allLinks(itemName, itemId, itemLink) VALUES(?, ?, ?)", (self.itemName, self.itemId, arg))
                self.db.commit()
                steamPageParser.getImgUrl(arg, f'{self.itemId}.png')

            self.sql.execute(f"SELECT fk_subscriberId FROM subscribers WHERE fk_subscriberId = '{self.userId[0]}' AND fk_allLinks_itemId = {self.itemId}")
            check = self.sql.fetchone()
            if check == None:
                self.sql.execute(f"INSERT INTO subscribers(fk_allLinks_itemId, fk_subscriberId) VALUES (?, ?)", (self.itemId, self.userId[0]))
                self.db.commit()
                return True
            return False
        else:
            return False


    def unsubscribe(self, login: int, arg):
        self.userId = BotDB().checkUser(login)
        self.itemId = steamPageParser.itemId(arg)
        self.itemName = steamPageParser.itemName(arg)
        if self.itemId == 'Error' or self.itemName == 'Error':
            return "Wrong usage"
        if self.userId != None:
            self.sql.execute(f"SELECT * FROM subscribers WHERE fk_subscriberId = '{self.userId[0]}' AND fk_allLinks_itemId = '{self.itemId}'")
            check = self.sql.fetchone()
            if check != None:
                self.sql.execute(f"DELETE FROM subscribers WHERE fk_subscriberId = {self.userId[0]} AND fk_allLinks_itemId = '{self.itemId}'")
                self.db.commit()
                return True
            return False
        else:
            return False


    def getPriceAndDate(self, itemId):
        self.sql.execute(f"SELECT price from allLinks WHERE itemId = '{itemId}'")
        self.price = self.sql.fetchone()
        self.sql.execute(f"SELECT lastDatePrice from allLinks WHERE itemId = '{itemId}'")
        self.lastDatePrice = self.sql.fetchone()
        return [self.price, self.lastDatePrice]
# test = SubsDB()
# url = 'https://steamcommunity.com/market/listings/570/Commodore%27s%20Sash'
# print(test.subscribe(277809275, url))




# получение всех img всех подписок
# test = SubsDB()
# a = test.receiveItemIds()
# b = test.receiveItemUrls()
# for i in range(len(a)):
#     id = a[i][0]
#     print(id)
#     url = b[i][0]
#     print(url)
#     steamPageParser.getImgUrl(str(url), str(id))


'''    def findAccount(self, login: str):
        self.sql.execute(f"SELECT * FROM accounts WHERE login = '{login}'")
        return self.sql.fetchone()
        '''

# test = BotDB()
# print(test.findAccount('steafar1'))
# test.insertData('accounts', 'steafar1', 'lastUserId', '123')
# print(test.findAccount('steafar1'))
# test.insertData('accounts', 'steafar1', 'lastTimeRequest', 'sdhfukjsd')
# print(test.findAccount('steafar1'))