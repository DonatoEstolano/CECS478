import tkinter
import requests
import ChatAppTwo
import hmactoserver
import os
from tkinter import Toplevel

def mainWindow():
    window = tkinter.Tk() # Creates a GUI window
    window.title("Chat Application") # Applies window name
    window.resizable(width="False", height="False") # Prevents resizing

    mainFrame = tkinter.Frame(window, width=400, height=400)
    mainFrame.pack()

    titleFrame = tkinter.Frame(mainFrame)
    titleFrame.place(width=200, height=100, x=100, y=100)

    infoFrame = tkinter.Frame(mainFrame)
    infoFrame.place(width=250, height=250, x=75, y=200)

    title = tkinter.Label(titleFrame, text="478 Chat", font=("Arial", 40))
    title.pack()

    usernameLabel = tkinter.Label(infoFrame, text="Username: ", font="Arial")
    usernameLabel.grid(row=0, column=0)

    userEntry = tkinter.StringVar()
    usernameEntry = tkinter.Entry(infoFrame, width=15, textvariable=userEntry)
    usernameEntry.grid(row=0, column=1)

    passwordLabel = tkinter.Label(infoFrame, text="Password: ", font="Arial")
    passwordLabel.grid(row=1, column=0)

    pwEntry = tkinter.StringVar()
    passwordEntry = tkinter.Entry(infoFrame, width=15, show="*", textvariable=pwEntry)
    passwordEntry.grid(row=1, column=1)

    blankOne = tkinter.Label(infoFrame)
    blankOne.grid(row=2, column=0)

    blankTwo = tkinter.Label(infoFrame)
    blankTwo.grid(row=2, column=1)

    def register():
        site = 'https://www.cecs-478.me/register'
        payload = {'username': userEntry.get(), 'password': pwEntry.get()}
        regRequest = requests.post(url=site, data=payload)
        regjson = regRequest.json()

        if regjson['success'] == True: 
            tokenPath = os.path.join(os.getcwd(), (userEntry.get() + "token.txt"))
            tokenFile = open(tokenPath, "w")
            tokenFile.write(regjson['token'])
            tokenFile.close()

            swindow = Toplevel()

            regMsg = tkinter.Label(swindow, text=regjson['message'])
            regMsg.pack()

            def toChat():
                swindow.destroy()
                window.destroy()
                ChatAppTwo.mainWindow(userEntry.get(), regjson['token'])

            contButton = tkinter.Button(swindow, text="OK", command=toChat)
            contButton.pack()

            swindow.mainloop()
        else:
            ewindow = Toplevel()

            errMsg = tkinter.Label(ewindow, text=regjson['message'])
            errMsg.pack()

            def toMain():
                ewindow.destroy()

            contButton = tkinter.Button(ewindow, text="OK", command=toMain)
            contButton.pack()

            ewindow.mainloop()

    registerButton = tkinter.Button(infoFrame, text="Register", width=8, command=register)
    registerButton.grid(row=3, column=0)

    def login():
        site = 'https://www.cecs-478.me/challenge'
        payload = {'username': userEntry.get()}
        regRequest = requests.post(url=site, data=payload)
        regjson = regRequest.json()

        responset = hmactoserver.response(pwEntry.get(), regjson['salt'], regjson['challenge'])

        site = 'https://www.cecs-478.me/login'
        payload = {'username': userEntry.get(), 'response': responset}
        regRequesttwo = requests.post(url=site, data=payload)
        regjsontwo = regRequesttwo.json()

        if regjsontwo['success'] == True:
            tokenPath = os.path.join(os.getcwd(), (userEntry.get() + "token.txt"))
            tokenFile = open(tokenPath, "w")
            tokenFile.write(regjsontwo['token'])
            tokenFile.close()

            swindow = Toplevel()

            regMsg = tkinter.Label(swindow, text=regjsontwo['message'])
            regMsg.pack()

            def toChatTwo():
                swindow.destroy()
                window.destroy()
                ChatAppTwo.mainWindow(userEntry.get(), regjsontwo['token'])

            contButton = tkinter.Button(swindow, text="OK", command=toChatTwo)
            contButton.pack()

            swindow.mainloop()
        else:
            ewindow = Toplevel()

            errMsg = tkinter.Label(ewindow, text=regjsontwo['message'])
            errMsg.pack()

            def toMainTwo():
                ewindow.destroy()

            contButton = tkinter.Button(ewindow, text="OK", command=toMainTwo)
            contButton.pack()

            ewindow.mainloop()

    loginButton = tkinter.Button(infoFrame, text="Login", width=8, command=login)
    loginButton.grid(row=3, column=1)

    window.mainloop()

def main():
    mainWindow()

main()