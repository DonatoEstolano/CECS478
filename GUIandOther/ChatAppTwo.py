import tkinter
import requests
import Secret
import os
from tkinter import Toplevel

def mainWindow(username, token):
    window = tkinter.Tk() # Creates a GUI window
    window.title("Chat Application") # Applies window name
    window.resizable(width="False", height="False") # Prevents resizing

    mainFrame = tkinter.Frame(window, width=400, height=400)
    mainFrame.pack()

    titleFrame = tkinter.Frame(mainFrame)
    titleFrame.place(width=200, height=100, x=100, y=10)

    infoFrame = tkinter.Frame(mainFrame)
    infoFrame.place(width=250, height=250, x=75, y=100)

    title = tkinter.Label(titleFrame, text=("Logged in as: " + username), font=("Arial", 12))
    title.pack()

    chatwithlabel = tkinter.Label(titleFrame, text="Chat with: ", font=("Arial", 15))
    chatwithlabel.pack()

    chatEntry = tkinter.StringVar()
    chatwith = tkinter.Entry(titleFrame, width=15, textvariable=chatEntry)
    chatwith.pack()

    scrollbar = tkinter.Scrollbar(infoFrame)
    scrollbar.pack(side="right", fill="y")

    def getMessage(event):
        #privateFilePath = "/Users/estolanod/Desktop/CECS 478 Fall 2018/private.pem" # File path to the private pem file path
        privateFilePath = os.path.join(os.getcwd(), "private.pem")
        site = 'https://www.cecs-478.me/receive'
        tokent = {'x-access-token': token}
        payload = {'receiver': username}
        regRequest = requests.get(url=site, headers=tokent, data=payload)

        if regRequest.status_code == 200:
            actualMsg = Secret.Decrypter(regRequest.json(), privateFilePath)

            chat.insert(tkinter.END, (chatEntry.get() + ": " + actualMsg.decode('utf-8')))

    chat = tkinter.Listbox(infoFrame, font="Arial", height=12, width=200)
    chat.bind("<Enter>", getMessage)
    chat.bind("<Leave>", getMessage)
    chat.pack()

    chat.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=chat.yview)

    messageEntry = tkinter.StringVar()
    message = tkinter.Entry(infoFrame, width=25, textvariable=messageEntry)
    message.bind("<Enter>", getMessage)
    message.bind("<Leave>", getMessage)
    message.pack()

    def sendmessage():
        #pemFilePath = "/Users/estolanod/Desktop/CECS 478 Fall 2018/public.pem"
        pemFilePath = os.path.join(os.getcwd(), "public.pem")

        plain = messageEntry.get().encode('utf-8')
        (ciphertext, bothkeys, hmac, random) = Secret.Encrypter(plain, pemFilePath)

        site = 'https://www.cecs-478.me/send'
        tokent = {'x-access-token': token}
        payload = {'message': ciphertext, 'sender': username, 'receiver': chatEntry.get(), 'keys': bothkeys, 'tag': hmac, 'iv': random}
        regRequest = requests.post(url=site, headers=tokent, data=payload)
        regjson = regRequest.json()

        if regjson['success'] == True:
            chat.insert(tkinter.END, (username + ": " + messageEntry.get()))
        else:
            ewindow = Toplevel()

            errMsg = tkinter.Label(ewindow, text=regjson['message'])
            errMsg.pack()

            def toMainTwo():
                ewindow.destroy()

            contButton = tkinter.Button(ewindow, text="OK", command=toMainTwo)
            contButton.pack()

            ewindow.mainloop()

    sendEvent = tkinter.Button(infoFrame, text="Send", width=8, command=sendmessage)
    sendEvent.bind("<Enter>", getMessage)
    sendEvent.bind("<Leave>", getMessage)
    sendEvent.pack()

    window.mainloop()