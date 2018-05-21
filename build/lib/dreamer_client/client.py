"""
Функции клиента:​
- сформировать presence-сообщение;
- отправить сообщение серверу;
- получить ответ сервера;
- разобрать сообщение сервера;
- имеет ​​параметры ​к​омандной ​с​троки:
- -p ​​<port> ​-​ ​​TCP-порт ​​для ​​работы ​(​по ​у​молчанию ​​использует ​​порт ​​7777);
- -a ​​<adr> ​-​ ​I​P-адрес ​​для ​​прослушивания ​(​по ​у​молчанию ​с​лушает ​​все ​​доступные ​​адреса).
"""
import sys
import threading
import time
from errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, ResponseCodeError
from socket import socket, AF_INET, SOCK_STREAM
from jim.utils import send_message, get_message
from jim.config import *
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal
from queue import Queue

def create_message(message_to, login, text):
    return {ACTION: MESSAGE, TIME: time.time(), TO: message_to, FROM: login, MESSAGE: text}

class Receiver:
    ''' Класс-получатель информации из сокета
    '''
    def __init__(self, sock, request_queue):
        self.request_queue = request_queue
        self.sock = sock
        self.is_alive = False

    def process_message(self, message):
        pass

    def poll(self):
        self.is_alive = True
        while True:
            if not self.is_alive:
                break
            message = get_message(self.sock)
            print(message)
            try:
                if ACTION in message:
                    # print("\n>>", message)
                    # print('{} >> {}'.format(message[FROM], message[MESSAGE]))
                    self.process_message(message)
                else:
                    self.request_queue.put(message)
            except Exception as e:
                print(e)

    def stop(self):
        self.is_alive = False

class ConsoleReciever(Receiver):

    def process_message(self, message):
        print('{} << {}'.format(message[FROM], message[MESSAGE]))

class GuiReciever(Receiver, QObject):
    gotData = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, sock, request_queue):
        Receiver.__init__(self, sock, request_queue)
        QObject.__init__(self)

    def process_message(self, message):
        # text = '{} << {}'.format(message[FROM], message[MESSAGE])
        # self.gotData.emit(text)
        self.gotData.emit('{} << {}'.format(message[FROM], message[MESSAGE]))

    def poll(self):
        super().poll()
        self.finished.emit(0)

class Client:

    def __init__(self, login):
        # self.ip = ip
        # self.port = port
        self.login = login
        self.request_queue = Queue()

    def create_presence(self):
        # Если имя не строка
        if not isinstance(self.login, str):
            # Генерируем ошибку передан неверный тип
            raise TypeError
        # Если длина имени пользователя больше 25 символов
        if len(self.login) > 25:
            # генерируем нашу ошибку имя пользователя слишком длинное
            raise UsernameToLongError(self.login)
        # формируем словарь сообщения
        message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.login,
                'status': 'Yep, I am here!'
            }
        }
        print(message)
        return message

    def send_get(self, message):
        try:
            send_message(self.sock, message)
            resp = get_message(self.sock)
            # resp = self.translate_message(resp)
            print('Ответ сервера: ', resp)
            return resp
        except Exception as e:
            print(e)

    def get_contacts(self):
        message = {
            ACTION: 'get_contacts',
            TIME: time.time(),
            ACCOUNT_NAME: self.login
        }
        rsp = self.send_get(message)
        print('У вас : ', rsp['quantity'], 'контактов!')
        print('Ваши контакты: ')
        contacts = get_message(self.sock)
        print(contacts['user_id'])
        return contacts['user_id']

    def get_avatar(self):
        message = {
            ACTION: 'get_avatar',
            TIME: time.time(),
            ACCOUNT_NAME: self.login
        }
        rsp_avatar = self.send_get(message)
        print(rsp_avatar)
        return rsp_avatar

    def change_avatar(self, avatar_path):
        message = {
            ACTION: 'change_avatar',
            TIME: time.time(),
            ACCOUNT_NAME: self.login,
            AVATAR: avatar_path
        }
        send_message(self.sock, message)
        rsp_ch_avatar = self.request_queue.get()
        return rsp_ch_avatar

    def create_add_contact(self, nickname):
        # Если имя не строка
        if not isinstance(nickname, str):
            # Генерируем ошибку передан неверный тип
            raise TypeError
        # Если длина имени пользователя больше 25 символов
        if len(nickname) > 25:
            # генерируем нашу ошибку имя пользователя слишком длинное
            raise UsernameToLongError(nickname)
        # формируем словарь сообщения
        try:
            message = {
                ACTION: 'add_contact',
                TIME: time.time(),
                ACCOUNT_NAME: self.login,
                USER_ID: nickname
            }
            send_message(self.sock, message)
            rsp = self.request_queue.get()
            print(rsp)
            return rsp
        except Exception as e:
            print(e)

    def create_del_contact(self, nickname):
        message = {
            ACTION: 'del_contact',
            TIME: time.time(),
            ACCOUNT_NAME: self.login,
            USER_ID: nickname
        }
        send_message(self.sock, message)
        resp1 = self.request_queue.get()
        print(resp1)
        return resp1

    def translate_message(self, response):
        # Передали не словарь
        if not isinstance(response, dict):
            raise TypeError
        # Нету ключа response
        if RESPONSE not in response:
            # Ошибка нужен обязательный ключ
            raise MandatoryKeyError(RESPONSE)
        # получаем код ответа
        code = response[RESPONSE]
        # длина кода не 3 символа
        if len(str(code)) != 3:
            # Ошибка неверная длина кода ошибки
            raise ResponseCodeLenError(code)
        # неправильные коды символов
        if code not in RESPONSE_CODES:
            # ошибка неверный код ответа
            raise ResponseCodeError(code)
        # возвращаем ответ
        return response

    def start_session(self):
        self.sock = socket(AF_INET, SOCK_STREAM) # Создает сокет TCP
        # try:
        #     adr = sys.argv[1]
        # except IndexError:
        #     adr = 'localhost'
        # try:
        #     port = int(sys.argv[2])
        # except IndexError:
        #     port = 7777
        # except ValueError:
        #     print('Порт должен быть целым числом')
        #     sys.exit(0)
        self.sock.connect(('localhost', 7777))  # Соединиться с сервером
        message = self.create_presence()
        # send_message(self.sock, message)
        # response = get_message(self.sock)
        # response = self.translate_message(response)
        # print('Ответ сервера: ', response[RESPONSE])
        response = self.send_get(message)
        return response

    def end_session(self):
        self.sock.close()

if __name__ == '__main__':
    print('Эхо-клиент запущен!')
    try:
        login = sys.argv[1]
    except IndexError:
        login = 'Leo'
    client = Client(login)
    client.start_session()
    client.get_contacts()

    listener = ConsoleReciever(client.sock, client.request_queue)
    th_listen = threading.Thread(target=listener.poll)
    th_listen.daemon = True

    th_listen.start()

    client.end_session()
