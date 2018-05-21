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
import sys, os
import time

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QLineEdit, QFormLayout, QFileDialog, QAction

from errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, ResponseCodeError
from socket import socket, AF_INET, SOCK_STREAM
from jim.utils import send_message, get_message
from jim.config import *
from threading import Thread
from client import Client, GuiReciever, create_message
from PyQt5 import QtWidgets
import threading
from PyQt5.QtCore import QThread, pyqtSlot
import log_pass_form
import client_gui

# SMILE_URL = os.path.join(os.path.dirname(os.path.abspath(__file__)
#                 ), "img", "ab.gif")
# MELANCHOLY_URL = os.path.join(os.path.dirname(os.path.abspath(__file__)
#                 ), "img", "ac.gif")
# SURPRISE_URL = os.path.join(os.path.dirname(os.path.abspath(__file__)
#                 ), "img", "ai.gif")
# BOLD_URL = os.path.join(os.path.dirname(os.path.abspath(__file__)
#                 ), "img", "b.jpg")
# ITALIC_URL = os.path.join(os.path.dirname(os.path.abspath(__file__)
#                 ), "img", "i.jpg")
# UNDERLINED_URL = os.path.join(os.path.dirname(os.path.abspath(__file__)
#                 ), "img", "u.jpg")

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
ui = client_gui.Ui_MainWindow()
ui.setupUi(window)

def setLoginPassword():

    dialog = QtWidgets.QDialog()
    lp = log_pass_form.Ui_Dialog()
    lp.setupUi(dialog)

    lp.pushButtonCancel.clicked.connect(dialog.reject)
    lp.pushButtonOk.clicked.connect(dialog.accept)

    dialog.exec()

    login = lp.lineEditLogin.text()
    password = lp.lineEditPassword.text()
    user = {'login': login, 'password': password}
    # print(user)
    return user

def load_contacts(contacts):
    ui.listWidgetContacts.clear()
    for contact in contacts:
        ui.listWidgetContacts.addItem(contact)

@pyqtSlot(str)
def update_chat(data):
    ''' Отображение сообщения в истории
    '''
    try:
        msg = data
        ui.listWidgetChat.addItem(msg)
    except Exception as e:
        print(e)

def on_clicked_add():
    try:
        username = ui.lineEditContact.text()
        print(username)
        if username:
            client.create_add_contact(username)
            ui.listWidgetContacts.addItem(username)
        ui.lineEditContact.clear()
    except Exception as e:
        print(e)

ui.pushButtonAddContact.clicked.connect(on_clicked_add)

def on_clicked_del():
    try:
        """Удаление контакта"""
        # получаем выбранный элемент в QListWidget
        current_item = ui.listWidgetContacts.currentItem()
        # получаем текст - это имя нашего контакта
        username = current_item.text()
        # удаление контакта (отправляем запрос на сервер)
        client.create_del_contact(username)
        # удаляем контакт из QListWidget
        current_item = ui.listWidgetContacts.takeItem(ui.listWidgetContacts.row(current_item))
        del current_item
        # selectItems = ui.listWidgetContacts.selectedItems()
        # username = selectItems.text()
        # client.create_del_contact(username)
        # ui.listWidgetContacts.takeItem(ui.listWidgetContacts.row(selectItems))
    except Exception as e:
        print(e)

ui.pushButtonDelContact.clicked.connect(on_clicked_del)

def send_messange():
    try:
        current_item = ui.listWidgetContacts.currentItem()
        username = current_item.text()
        text = ui.lineEditMsg.text()
        if text:
            send_message(client.sock, create_message(username, login, text))
            msg = '{} >> {}'.format(login, text)
            ui.listWidgetChat.addItem(msg)
            ui.lineEditMsg.clear()
    except Exception as e:
        print(e)

ui.pushButtonSendMsg.clicked.connect(send_messange)

def showDialogAddAvatar():
    imageFile = QFileDialog.getOpenFileName(window, 'Open file')[0]
    load_avatar(imageFile)
    client.change_avatar(imageFile)

def load_avatar(imageFile):
    image = Image.open(imageFile)
    w, h = image.size
    k = w / h
    height = 121
    width = int(height * k)
    image = image.resize((width, height), Image.ANTIALIAS)
    # delta = (width - height) / 2
    # image = image.crop((delta, 0, height + delta, height))
    img_tmp = ImageQt(image.convert('RGBA'))
    print(img_tmp)
    pixmap = QPixmap.fromImage(img_tmp)
    print(pixmap)
    ui.labelAvatar.setPixmap(pixmap)

ui.pushButtonAddAvatar.clicked.connect(showDialogAddAvatar)

# def add_menu_item(item_image, item_name, toolbar, slot_func):
#     item = QAction(QIcon(item_image), item_name, window)
#     item.triggered.connect(slot_func)
#     toolbar.addAction(item)
#
# def action_Gif(url):
#     print('---')
#     try:
#         ui.lineEditMsg.textCursor().insertHtml('<img src="%s"/>' % url)
#     except Exception as e:
#         print(e)
#
# def action_format(tag):
#     print('---')
#     selected_text = ui.lineEditMsg.textCursor().selectedText()
#     ui.lineEditMsg.textCursor().insertHtml(
#         '<{tag}>{val}</{tag}>'.format(val=selected_text, tag=tag))
#
# add_menu_item(SMILE_URL, 'Smile', ui.toolbar, lambda: action_Gif(SMILE_URL))
# add_menu_item(MELANCHOLY_URL, 'Melancholy', ui.toolbar, lambda: action_Gif(MELANCHOLY_URL))
# add_menu_item(SURPRISE_URL, 'Surprise', ui.toolbar, lambda: action_Gif(SURPRISE_URL))
#
# add_menu_item(BOLD_URL, 'Bold', ui.toolbar, lambda: action_format('b'))
# add_menu_item(ITALIC_URL, 'Italic', ui.toolbar, lambda: action_format('i'))
# add_menu_item(UNDERLINED_URL, 'Underlined', ui.toolbar, lambda: action_format('u'))

user = setLoginPassword()
print(user)
if len(user['login']) != 0:
    login = user['login']
    print(login)
    ui.lineEditNickname.setText(login)
    client = Client(login)
    client.start_session()
    contact_list = client.get_contacts()
    print(contact_list)
    load_contacts(contact_list)
    client_avatar = client.get_avatar()
    print(client_avatar)
    load_avatar(client_avatar[AVATAR])

    listener = GuiReciever(client.sock, client.request_queue)
    listener.gotData.connect(update_chat)

    th = QThread()
    listener.moveToThread(th)

    th.started.connect(listener.poll)
    th.start()

    window.show()
    sys.exit(app.exec_())
