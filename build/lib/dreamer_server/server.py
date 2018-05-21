"""
Функции ​​сервера:​
- принимает ​с​ообщение ​к​лиента;
- формирует ​​ответ ​к​лиенту;
- отправляет ​​ответ ​к​лиенту;
- имеет ​​параметры ​к​омандной ​с​троки:
- -p ​​<port> ​-​ ​​TCP-порт ​​для ​​работы ​(​по ​у​молчанию ​​использует ​​порт ​​7777);
- -a ​​<adr> ​-​ ​I​P-адрес ​​для ​​прослушивания ​(​по ​у​молчанию ​с​лушает ​​все ​​доступные ​​адреса).
"""
import asyncio
import base64
import shutil
import sys
import json
import select
from socket import socket, AF_INET, SOCK_STREAM
from jim.utils import dict_to_bytes, bytes_to_dict, send_message, get_message
from jim.config import *
from repo.server_repo import *
from repo.server_models import *

def presence_response(presence_message):
    """
Формирование ответа клиенту
:param presence_message: Словарь presence запроса
:return: Словарь ответа
"""
# Делаем проверки
    if ACTION in presence_message and \
                presence_message[ACTION] == PRESENCE and \
                TIME in presence_message and \
                isinstance(presence_message[TIME], float):
    # Если всё хорошо шлем ОК
        username = presence_message[USER][ACCOUNT_NAME]
        ses = Repo(session)
        if not ses.client_exists(username):
            ses.add_client(username)
            session.close()
        return {RESPONSE: 200}, username
    else:
    # Шлем код ошибки
        return {RESPONSE: 400, ERROR: 'Не верный запрос'}

def change_avatar_responce(message):
    if ACTION in message and \
                message[ACTION] == 'change_avatar' and \
                TIME in message and \
                isinstance(message[TIME], float):
    # Если всё хорошо шлем ОК
        avatar_path = message[AVATAR]
        username = message[ACCOUNT_NAME]
        path_to_avatar = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "avatars", str(username))
        shutil.copy(avatar_path, path_to_avatar)
        return {RESPONSE: 202, MESSAGE: 'Аватар успешно изменен!'}
    else:
    # Шлем код ошибки
        return {RESPONSE: 400, ERROR: 'Не верный запрос'}

def add_contact_response(message):
    """
    Формирование ответа клиенту
    """
# Делаем проверки
    if ACTION in message and \
                message[ACTION] == 'add_contact' and \
                TIME in message and \
                isinstance(message[TIME], float):
    # Если всё хорошо шлем ОК
        user_id = message[USER_ID]
        username = message[ACCOUNT_NAME]
        ses = Repo(session)
        ses.add_contact(username, user_id)
        session.close()
        return {RESPONSE: 202, MESSAGE: 'Контакт успешно добавлен!'}
    else:
    # Шлем код ошибки
        return {RESPONSE: 400, ERROR: 'Не верный запрос'}

def del_contact_response(message):
    """
    Формирование ответа клиенту
    """
# Делаем проверки
    if ACTION in message and \
                message[ACTION] == 'del_contact' and \
                TIME in message and \
                isinstance(message[TIME], float):
    # Если всё хорошо шлем ОК
        user_id = message[USER_ID]
        username = message[ACCOUNT_NAME]
        ses = Repo(session)
        ses.del_contact(username, user_id)
        session.close()
        return {RESPONSE: 202, MESSAGE: 'Контакт успешно удален!'}
    else:
    # Шлем код ошибки
        return {RESPONSE: 400, ERROR: 'Не верный запрос'}

def get_contacts_responce(quantity):
    """
    Формирование ответа клиенту
    """
    # Делаем проверки
    # if ACTION in message and \
    #         message[ACTION] == 'get_contacts' and \
    #         TIME in message and \
    #         isinstance(message[TIME], float):
        # Если всё хорошо шлем ОК
    return {RESPONSE: 202, 'quantity': quantity}
    # else:
    #     # Шлем код ошибки
    #     return {RESPONSE: 400, ERROR: 'Не верный запрос'}

def get_contacts_rsp(nickname):
    return {'action': 'contact_list', 'user_id': nickname}

class Server:

    def start_server(self):
        sock = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
        # Получаем аргументы скрипта
        try:
            addr = sys.argv[1]
        except IndexError:
            addr = ''
        try:
            port = int(sys.argv[2])
        except IndexError:
            port = 7777
        except ValueError:
            print('Порт должен быть целым числом')
            sys.exit(0)
        # print(addr)
        # print(port)
        sock.bind((addr, port))
        sock.listen(5)
        sock.settimeout(0.2)
        clients = []
        names = {}
        while True:
            try:
                connect, addr = sock.accept()  # Принять запрос на соединение
                # получаем сообщение от клиента
                presence = get_message(connect)
                # print(presence)
                # # print(presence[USER][ACCOUNT_NAME])
                # # формируем ответ
                response, client_name = presence_response(presence)
                # # отправляем ответ клиенту
                send_message(connect, response)

                # msg1 = get_message(connect)
                # response2 = JIM_response()
                # resp2 = response2.del_contact_response(msg1)
                # send_message(connect, resp2)
                # print(presence[USER][ACCOUNT_NAME], msg1['user_id'])
                # if resp2[RESPONSE] == 202:
                #     self.del_contact_db(presence[USER][ACCOUNT_NAME], msg1['user_id'])
            except OSError as e:
                pass
            else:
                print("Получен запрос на соединение от %s" % str(addr))
                clients.append(connect)
                names[client_name] = connect
                print(names)
                print('К нам подключился {}'.format(client_name))
            finally:
                # Проверить наличие событий ввода-вывода
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(clients, clients, [], wait)
                    # print(w, r)
                except:
                    pass  # Ничего не делать, если какой-то клиент отключился
                response = self.read_requests(r, clients)  # Сохраним запросы клиентов
                self.write_responses(response, names, clients)  # Выполним отправку ответов клиентам

    def read_requests(self, r_clients, all_clients):
        ''' Чтение запросов из списка клиентов
        '''
        messages = []
        for sock in r_clients:
            try:
                message = get_message(sock)
                messages.append((message, sock))
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                all_clients.remove(sock)
        # print(messages)
        return messages

    def write_responses(self, messages, names, all_clients):
        ''' Эхо-ответ сервера клиентам, от которых были запросы
        '''
        # for sock in names:
        for message, sock in messages:
            try:
                print(message)
                print(sock)
                if message[ACTION] == 'get_contacts':
                    res = self.get_contacts(message[ACCOUNT_NAME])
                    # print(res)
                    rsp = get_contacts_responce(len(res))
                    send_message(sock, rsp)
                    contact_names = [contact.Name for contact in res]
                    # print(contact_names)
                    send_message(sock, get_contacts_rsp(contact_names))
                elif message[ACTION] == 'get_avatar':
                    res_avatar = self.get_avatar(message[ACCOUNT_NAME])
                    print(res_avatar)
                    send_message(sock, res_avatar)
                elif message[ACTION] == 'change_avatar':
                    rsp_ch_av = change_avatar_responce(message)
                    print(rsp_ch_av)
                    send_message(sock, rsp_ch_av)
                elif message[ACTION] == 'add_contact':
                    rsp1 = add_contact_response(message)
                    send_message(sock, rsp1)
                elif message[ACTION] == 'del_contact':
                    rsp2 = del_contact_response(message)
                    send_message(sock, rsp2)
                elif message[ACTION] == MESSAGE:
                    to = message[TO]
                    sock = names.get(to)
                    # print(sock)
                    # for sock in all_clients:
                    send_message(sock, message)
            except:                 # Сокет недоступен, клиент отключился
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                sock.close()
                all_clients.remove(sock)

    # def add_client_db(self, client):
    #     ses = Repo(session)
    #     chek = ses.client_exists(client)
    #     if chek == 0:
    #         ses.add_client(client)
    #         session.close()
    #     else:
    #         session.close()

    # def add_contact_db(self, client, contact):
    #     ses = Repo(session)
    #     ses.add_contact(client, contact)
    #     session.close()

    def del_contact_db(self, client, contact):
        ses = Repo(session)
        ses.del_contact(client, contact)
        session.close()

    def get_contacts(self, client):
        ses = Repo(session)
        res = ses.get_contacts(client)
        session.close()
        return res

    def get_avatar(self, client):
        avatar_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "avatars", str(client))
        if os.path.isfile(avatar_path):
            return {RESPONSE: 202, AVATAR: avatar_path}
        else:
            avatar_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)
                ), "avatars", "default_avatar.png")
            return {RESPONSE: 202, AVATAR: avatar_path}


print('Эхо-сервер запущен!')
server = Server()
server.start_server()

