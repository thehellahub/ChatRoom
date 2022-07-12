import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout, QMessageBox, QAction
from PyQt5 import QtGui
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic, QtWidgets
from PyQt5 import QtGui
import inspect
import socket
from threading import Thread
import time
import Client


# Pointing to my GUI blueprint file
Ui_MainWindow, QtBaseClass = uic.loadUiType("Login_GUI.ui")


class LoginApp(QtWidgets.QMainWindow):

    client_socket = None

    def __init__(self, parent=None):

        try:

            # Loading the GUI file 'Login_GUI.ui'
            super(LoginApp, self).__init__()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

            # Setting password text field to not show the password when entered
            self.ui.password_text.setEchoMode(QtWidgets.QLineEdit.Password)

            # Creating socket object
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except Exception as e:
                print("\n Socket creation failed. Error: ")
                print(e)
                self.ui.TextArea.setPlainText(str(e))

            # Getting host ip for socket
            try:
                host_url = 'www.goatgoose.com'
                host_ip = socket.gethostbyname(host_url)
            except Exception as e:
                print("\n Error ocurred resolving the host. Error: ")
                print(e)
                self.ui.TextArea.setPlainText(str(e))

            # connecting to the server ip address on specified port
            try:
                port = 12000
                s.connect((host_ip, port))
            except Exception as e:
                print("\n\n Couldn't connect socket to Host IP: " + str(host_ip) + " at port number: " + str(port) + ". Error: ")
                print(str(e))

            # Handshake
            try:
                handshake_string = 'HELLO\n'
                s.send(handshake_string.encode())
                response = s.recv(1024).decode()
                #print(response)

                if str(response).strip() == 'HELLO':
                    self.ui.TextArea.setPlainText("Socket connection to www.goatgoose.com Successful!")
                else:
                    print("Socket connection to www.goatgoose.com Unsuccessful. Please restart program.")
                    
                    # Setting the system report text area
                    self.ui.TextArea.setPlainText("Socket connection to www.goatgoose.com Unsuccessful. Please restart program.")
                    
                    # Creating a dialog box to alert the user that the socket broke
                    close = QtWidgets.QMessageBox.warning(self,
                                                        "Broken Socket. Program aborted. Please restart application.",
                                                        "Broken Socket. Program aborted. Please restart application.",
                                                        QtWidgets.QMessageBox.Ok)
                    # When the user clicks ok...
                    if close == QtWidgets.QMessageBox.Ok:
                        sys.exit()
                        return

            except Exception as e:
                print("\n Handshake failed. Error: ")
                print(e)
                self.ui.TextArea.setPlainText("Handshake to www.goatgoose.com failed. Error: \n" + str(e))

            # Setting global socket variable to be the socket created above
            LoginApp.client_socket = s

        except Exception as e:
            print(e)
            self.ui.TextArea.setPlainText(str(e))


        # Setting login_button listener
        self.ui.login_button.clicked.connect(self.login)

        # Adding AOL running man (LOL RIP)
        # 175W 155H
        pixmap = QPixmap('AOL.jpg')
        self.ui.AOL_Label.setPixmap(pixmap)

# end init

    def login(self):

        # Getting user input from the fields
        user = self.ui.user.text()
        password = self.ui.password_text.text()

        try:
            login_string = 'AUTH:' + user + ':' + password + "\n"   # Prepping the login string to send through the socket
            LoginApp.client_socket.send(login_string.encode())      # Sending the string to the socket
            response = LoginApp.client_socket.recv(1024).decode()   # getting the response from the socket
            


            # Handling the response string with how the GUI should respond

            if str(response).strip() == 'AUTHYES':
                response = LoginApp.client_socket.recv(1024).decode()
                self.ui.TextArea.setPlainText(str("Login success. Welcome Online " + str(user)))


                # Open the main client GUI if successful login
                dialog = QtWidgets.QMainWindow()
                args=[LoginApp.client_socket, user]
                temp = self.dialog = Client.ClientApp(dialog, args=args)
                self.dialog.show()
                self.close_me()

            # Bad login
            elif str(response).strip() == 'AUTHNO':
                print('\n ERROR: INCORRECT PASSWORD.')

                self.ui.TextArea.setPlainText(str("Error Occurred: \n\nIncorrect Username or Password. Please try again."))
                
                # Create dialgue box to notify user of inproper login
                close = QtWidgets.QMessageBox.warning(self,
                                                        "Incorrect Username or Password!",
                                                        "Incorrect Username or Password! Connection refused.",
                                                        QtWidgets.QMessageBox.Ok)
                if close == QtWidgets.QMessageBox.Ok:
                    pass
                    return

            # User already logged in
            elif str(response).strip() == 'UNIQNO':
                print('\n ERROR: ALREADY LOGGED IN.')

                self.ui.TextArea.setPlainText(str("Error Occurred: \n\nUser already logged in. Please try again."))
                

                # Create dialgue box to notify user of inproper login
                close = QtWidgets.QMessageBox.warning(self,
                                                        "User already logged in! Connection refused.",
                                                        "User already logged in! Connection refused.",
                                                        QtWidgets.QMessageBox.Ok)
                if close == QtWidgets.QMessageBox.Ok:
                    pass
                    return
            else:
                self.ui.TextArea.setPlainText(str("Unknown Error Occurred"))
                return

        except Exception as e:
            print("\n Login failed. Error:")
            print(e)
            self.ui.TextArea.setPlainText(str("Please restart program.\n\nError Occurred: \n\n" + str(e)))

# end login
    
    # Close the GUI window
    def close_me(self):
        self.close()

# end close_me

# end Class LoginApp

# Kicking off the login GUI
class ChatApp:

    def go():
        app = QApplication(sys.argv)
        window = LoginApp()
        window.show()
        sys.exit(app.exec_())

# end Class ChatApp

#(EOF)

