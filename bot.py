from main import Main
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import warnings
from db import BotDB, SubsDB
from config import read_config
import datetime
import time
import requests
from requests.adapters import ReadTimeoutError
import steamPageParser
from threading import Thread
import os



### Token ###
vk_session = vk_api.VkApi(token=read_config()[0])  # Токен
#############

### Bot's Class ###
class VkBot():
    def __init__(self, token):
        self.token = token
        self.db = BotDB()
        self.subsDB = SubsDB()
        self.admins = read_config()[1]
        print(self.admins)
        # print(self.db.SDAusers())

    def getUserName(self, userId):
        self.vk = vk_session.get_api()
        user_get = self.vk.users.get(user_ids=(userId))[0]
        return f"{user_get['first_name']} {user_get['last_name']}"

    def _new_message(self, message): # Получение нового сообщения
        self.userId = event.user_id
        print(f"Сообщение от: {self.userId}: {message}\n")
        self.userMessageContext = message.split(' ')
        self.userMessageContext[0] = self.userMessageContext[0].lower()

        self.db.checkUser(self.userId, reg=True)
        self.commands = self.Commands(self.token, self.userId, self.admins)

        if self.commands.commandlist(self.userMessageContext[0].lower()) != None:
            self.commands.executeCommand(self.userMessageContext)
        else:
            self._send("Не понимаю. Попробуй использовать команду /help")


    def _send(self, message): # Отправка сообщения
        self.token.method('messages.send', {'user_id': self.userId, 'message': message, 'random_id': 0})


    def subscribeMailing(self, cur=False):
        currentTime = datetime.datetime.today().strftime("%d.%m.%Y - %H:%M:%S")
        currentTimeFormatted = datetime.datetime.strptime(currentTime, "%d.%m.%Y - %H:%M:%S")
        def calcPercent(currentPrice, lastCheckedPrice):
            if lastCheckedPrice[0][0] and lastCheckedPrice[1][0] != 'Null':
                currentPrice = float(currentPrice.replace('$', ''))
                lastCheckedDate = lastCheckedPrice[1][0]
                lastCheckedPrice = float(lastCheckedPrice[0][0].replace('$', ''))

                calc = (currentPrice / lastCheckedPrice) * 100 - 100
                lastCheckedTime = datetime.datetime.strptime(f"{lastCheckedDate}", "%d.%m.%Y - %H:%M:%S")
                timeDifference = currentTimeFormatted - lastCheckedTime
                timeDifference = timeDifference.total_seconds()/60/60
                if calc < 0: return f"{round(calc, 2)}% за {int(timeDifference)} часов"
                if calc > 0: return f"+{round(calc, 2)}% за {int(timeDifference)} часов"
                if calc == 0: return f"+{round(calc, 2)}% за {int(timeDifference)} часов"
            else:
                return 'нет информации'

        if cur == False: # Если рассылка массовая, по всем подписчикам
            self.subscriptions = self.subsDB.receiveUsers()
            for i in range(len(self.subscriptions)):
                self.data = self.subscriptions[i]
                self.itemId = self.data[0][0]
                self.itemName = self.subsDB.getItemName(self.itemId)
                self.url = self.subsDB.getUrl(self.itemId)
                self.currentprice = steamPageParser.jsonReceiver(self.itemId)
                self.lastCheckedPrice = self.subsDB.getPriceAndDate(self.itemId) # Массив с последней ценой и датой занесения её в бд / [1.23, 01.01.21]
                print(self.data)
                self.percent = calcPercent(self.currentprice, self.lastCheckedPrice)
                self.subsDB.insertData("allLinks", self.itemId, "price", self.currentprice)
                self.subsDB.insertData("allLinks", self.itemId, "lastDatePrice", currentTime)
                self.img = f'imgs/{self.itemId}.png'

                for k in range(len(self.subscriptions[i][1])):
                    self.userId = self.db.findUserById(self.subscriptions[i][1][k][0])
                    if os.path.isfile(f'imgs/{self.itemId}.png'):
                        a = vk_session.method("photos.getMessagesUploadServer")
                        b = requests.post(a['upload_url'], files={'photo': open(f'imgs/{self.itemId}.png', 'rb')}).json()
                        c = vk_session.method('photos.saveMessagesPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[0]
                        d = "photo{}_{}".format(c["owner_id"], c["id"])

                        message = f'⚠{self.itemName}⚠\n Цена на данный момент - {self.currentprice} ({self.percent})\n\n{self.url}\n'
                        self.token.method('messages.send', {'user_id': int(self.userId[0]), 'message': message, "attachment": d, "random_id": 0})
                    else:
                        message = f'⚠{self.itemName}⚠\n Цена на данный момент - {self.currentprice}\n\n{self.url}\n'
                        print(self.userId)
                        self.token.method('messages.send', {'user_id': int(self.userId[0]), 'message': message, 'random_id': 0})

        if cur == True: # Если пользователь запрашивает инфу
            self.userId = event.user_id
            self.id = self.db.checkUser(self.userId)
            self.subscriptions = self.subsDB.receiveUsersById(self.id[0])
            print(self.subscriptions)
            print('!!!')
            for i in range(len(self.subscriptions)):
                self.itemId = self.subscriptions[i][0] # Id предмета
                self.itemName = self.subsDB.getItemName(self.itemId) # Название предмета
                self.url = self.subsDB.getUrl(self.itemId) # URL предмета
                self.currentprice = steamPageParser.jsonReceiver(self.itemId)
                self.lastCheckedPrice = self.subsDB.getPriceAndDate(self.itemId)  # Массив с последней ценой и датой занесения её в бд / [1.23, 01.01.21]\
                self.percent = calcPercent(self.currentprice, self.lastCheckedPrice)
                self.img = f'imgs/{self.itemId}.png'
                if os.path.isfile(f'imgs/{self.itemId}.png'):
                    a = vk_session.method("photos.getMessagesUploadServer")
                    b = requests.post(a['upload_url'], files={'photo': open(f'imgs/{self.itemId}.png', 'rb')}).json()
                    c = vk_session.method('photos.saveMessagesPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[0]
                    d = "photo{}_{}".format(c["owner_id"], c["id"])
                    message = f'⚠{self.itemName}⚠\n Цена на данный момент - {self.currentprice} ({self.percent})\n\n{self.url}\n'
                    vk_session.method("messages.send", {"peer_id": int(self.userId), "message": message, "attachment": d, "random_id": 0})
                else:
                    message = f'⚠{self.itemName}⚠\n Цена на данный момент - {self.currentprice} ({self.percent})\n\n{self.url}\n'
                    self.token.method('messages.send', {'user_id': int(self.userId), 'message': message, 'random_id': 0})

    ### Commands ###
    class Commands():
        def __init__(self, token, userId, admins):
            self.commands = {'/acc': [1, self.acc], '/help': [0, self.help], '/sub': [1, self.sub], '/unsub': [1, self.unsub], '/mysubs': [0, self.mysubs], '/addsda': [1, self.addsda], '/remsda': [1, self.remsda], '/sdausers': [0, self.sdausers], '/showusers': [0, self.showusers]}
            self.db = BotDB()
            self.subsDB = SubsDB()
            self.token = token
            self.userId = userId
            self.Main = Main()
            self.admins = admins


        def commandlist(self, arg):
            if str(arg) in self.commands:
                return 'OK'


        def executeCommand(self, arg):
            if self.commands[arg[0]][0] == 0: self.commands[arg[0]][1]()
            if self.commands[arg[0]][0] > 0: self.commands[arg[0]][1](arg)



        def acc(self, arg):
            if len(arg) > 1: self.login = arg[1].lower()
            else:
                self.encorrectSyntax('acc')
                return
            if self.db.findAccount(self.login) != None:
                if self.db.checkSDA(self.userId) == True:
                    self.data = self.db.findAccount(self.login)
                    a = '\n'
                    self._send(f"⚠Данные аккаунта⚠\n Логин: {self.data[1]}\n Пароль: {self.data[2].replace(f'{a}', '')}\n 2FA: {self.Main.executeSDA(self.login)}\n\n❓Инфо❓\nПоследний пользователь: {self.data[4]}, {self.data[5]}")
                    self.db.insertData('accounts', self.data[1], 'lastUserId', VkBot(vk_session).getUserName(self.userId))
                    self.db.insertData('accounts', self.data[1], 'lastTimeRequest', datetime.datetime.today().strftime("%d.%m.%Y - %H:%M:%S"))
                else:
                    self._send("Нет прав")
            else:
                self._send("Такого аккаунта нет")
                return


        def addsda(self, arg):
            if len(arg) <= 1: self._send('Введите аргумент')
            else:
                if self.userId in self.admins:
                    if arg[1].isdigit():
                        status = self.db.addsda(arg[1])
                        if status == True:
                            self._send(f"Пользователь с ID {arg[1]} успешно добавлен в базу SDA и теперь может использовать аккаунты.")
                        elif status == 'Already':
                            self._send(f"Пользователь с ID {arg[1]} уже в БД.")
                        else:
                            self._send("Пользователя нет в БД пользователей.")
                    else:
                        self._send("Введите цифровой ID")
                else: self._send("Нет прав")


        def remsda(self, arg):
            if len(arg) <= 1: self._send('Введите аргумент')
            else:
                if self.userId in self.admins:
                    if arg[1].isdigit():
                        status = self.db.remsda(arg[1])
                        if status == True:
                            self._send(f"Пользователь с ID {arg[1]} удалён из базы SDA.")
                        elif status == 'Already':
                            self._send(f"Пользователь с ID {arg[1]} уже удалён из БД.")
                        else:
                            self._send("Пользователя нет в БД пользователей.")
                    else:
                        self._send("Введите цифровой ID")
                else: self._send("Нет прав")


        def sdausers(self):
            if self.userId in self.admins:
                out = ''
                self.users = self.db.showsdausers()
                for i in range(len(self.users)):
                    self.id = self.users[i][0]
                    self.vkId = self.db.findUserById(self.users[i][1])[0]
                    self.name = VkBot(vk_session).getUserName(self.vkId)
                    out = out + f"{self.id}:\n Имя: {self.name}\n VkID: {self.vkId}\n\n"
                if out != '':
                    self._send(f"{out}")
                else: self._send("Нет пользователей")
            else: self._send("Нет прав")


        def showusers(self):
            if self.userId in self.admins:
                out = ''
                self.users = self.db.showUsers()
                for i in range(len(self.users)):
                    self.id = self.users[i][0]
                    self.vkId = self.users[i][1]
                    self.name = VkBot(vk_session).getUserName(self.vkId)
                    out = out + f"{self.id}:\n Имя: {self.name}\n VkID: {self.vkId}\n\n"
                if out != '':
                    self._send(f"{out}")
                else: self._send("Нет пользователей")
            else: self._send("Нет прав")


        def sub(self, arg):
            if len(arg) <= 1:
                self.encorrectSyntax('sub')
                return
            self.result = self.subsDB.subscribe(self.userId, f"{arg[1]}")
            if self.result == True:
                self._send("Вы успешно подписались на ежедневное оповещение.")
            elif self.result == "Wrong usage":
                self._send("Пришлите ссылку на Steam предмет!")
            else:
                self._send("Вы уже имеете подписку.")


        def unsub(self, arg):
            if len(arg) <= 1:
                self.encorrectSyntax('unsub')
                return
            self.result = self.subsDB.unsubscribe(self.userId, f"{arg[1]}")
            if self.result == True:
                self._send("Вы успешно отписались от ежедневного оповещения на данный предмет.")
            elif self.result == "Wrong usage":
                self._send("Пришлите ссылку на Steam предмет!")
            else:
                self._send("Вы не подписаны на ежедневные оповещения по данному предмету.")

        def mysubs(self):
            VkBot(vk_session).subscribeMailing(cur=True)


        def help(self):
            a = '________________________________'
            self._send(f"🤖Команды бота🤖\n\n{a}\n🕵‍♀SDA🕵‍♀\n{self.encorrectSyntax('acc', error=False)}\n{a}\n🔔Подписка на уведомления вещей Steam🔔\n{self.encorrectSyntax('sub', error=False)}\n{self.encorrectSyntax('unsub', error=False)}\n{a}\n❓ПРОЧЕЕ❓\n/help - справочник команд")


        def _send(self, message):  # Отправка сообщения
            self.token.method('messages.send', {'user_id': self.userId, 'message': message, 'random_id': 0})


        def encorrectSyntax(self, funcName, error=True):
            self.syntaxErrorMsg = 'Ошибка: неправильный синтаксис.\nИспользование: '
            self.funcs = {'acc': "/acc (логин аккаунта)", 'sub': "/sub (ссылка на вещь с ТП Steam)", 'unsub': "/unsub (ссылка на вещь с ТП Steam)"}
            if error == True: self._send(f"{self.syntaxErrorMsg} {self.funcs[funcName].capitalize()}")
            else: return self.funcs[funcName]


###########


### Bot loader ###
class Starter():

    def startBot(self):
        try:
            bot = VkBot(vk_session)
            longpoll = VkLongPoll(vk_session)
            print("Бот запущен")
        except requests.exceptions.ConnectionError:
            print(f'{datetime.datetime.today()}: Ошибка при подключении к LongPoll. Возможно, отключен интернет.')

        while True:
            try:
                warnings.simplefilter('ignore', category=UserWarning)
                global event
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            message = event.text
                            bot._new_message(message)

            except NameError:
                print(f'{datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S")}: LongPoll не определён.\nПереподключение через 10 секунд\n')
                time.sleep(10)
            # except:
            #     print(f'{datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S")}: Проблема с подключением.\nПереподключение через 10 секунд\n')
            #     time.sleep(10)
            #     continue

    def timeCheck(self):
        timeList = ['0900', '1800', '0000', '1319']
        while True:
            if datetime.datetime.today().strftime("%H%M") in timeList:
                VkBot(vk_session).subscribeMailing()
                time.sleep(70)
            time.sleep(7)
##################

if __name__ == '__main__':
    Thread(target = Starter().startBot).start()
    Thread(target = Starter().timeCheck).start()

#print(VkBot().subscribeMailing())
