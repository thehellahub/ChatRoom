import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout, QMessageBox, QAction
from PyQt5 import QtGui
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic, QtWidgets
from PyQt5 import QtGui
import inspect
import socket
from threading import Thread
import time
from datetime import datetime


# Pointing to my GUI blueprint file
Ui_MainWindow, QtBaseClass = uic.loadUiType('Client_GUI.ui')


class ClientApp(QtWidgets.QMainWindow):


# Global Variables
	client_socket = None
	user = None
	online_users = None

	refresh_warning_label_on = False

	def __init__(self, parent=None, args=None):

	# starting up the GUI
		super(ClientApp, self).__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

	# getting the socket object passed forward from the login page
		ClientApp.client_socket = args[0]
		ClientApp.user = args[1]

	# Setting the text area global variables (helps with threading)
		ClientApp.list_users_text_area = self.ui.online_users

	# Setting QLabel to say who's logged in
		self.ui.logged_in_as.setText("Logged in as: " + str(ClientApp.user))


	# Setting logout_button listener
		self.ui.logout_button.clicked.connect(self.logout)


	# Creating listening thread for all incoming messages
		thread1 = Thread(target=ClientApp.listen_for_incoming_messages, args=(self,))
		thread1.start()

	# Setting function (listener) to list users 'refresh' button
		self.ui.refreshUsers.clicked.connect(self.listen_for_new_users)

	# Setting list of online users under respected text area
		list_users_string = 'LIST\n'
		ClientApp.client_socket.send(list_users_string.encode())
		self.ui.online_users.setText("Loading...")
		time.sleep(1)
		# Formatting the string
		ClientApp.online_users = str(ClientApp.online_users).strip()
		ClientApp.online_users = ClientApp.online_users.replace(",", "\n")
		self.ui.online_users.setText(ClientApp.online_users)

	# Setting function (listener) to the send message button
		self.ui.sendButton.clicked.connect(self.send_message)

	# Styling the refresh user list warning label
		self.ui.refresh_warning_label.setStyleSheet('color: red')
		self.ui.refresh_warning_label.hide()



# end init

	def logout(self):

		# Opening logout dialogue
		close = QtWidgets.QMessageBox.warning(self,
											"Are you sure you want to log out? Logging out will close the program.",
											"Are you sure you want to log out? Logging out will close the program.",
											QtWidgets.QMessageBox.Ok)
		if close == QtWidgets.QMessageBox.Ok:
			ClientApp.client_socket.send(b'BYE\n') # Sending the bye string to the socket
			ClientApp.client_socket.close() # closing the socket
			sys.exit() # Exiting the program
# end logout

	def listen_for_incoming_messages(self):
		try:
			while True:

				self.ui.messageBoard.repaint() # redraw the incoming messages board

				# Creating a datetime string
				now = datetime.now()
				dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

				# The constant reading from the socket 'response' string
				response = ClientApp.client_socket.recv(1024).decode()

				# Whether or not to show the Refresh Recommended label (When new user logs in/out)
				if ClientApp.refresh_warning_label_on == False:
					self.ui.refresh_warning_label.hide()

				if (len(response) > 0):

					# print("\nFrom listen_for_incoming_messages: ")
					# print(response)
					
					# don't print responses from the 'LIST' command
					if ( (':' in str(response).strip()) == False ):
						ClientApp.online_users = str(response)
						pass

					# String formatting, getting rid of the 'From:' portion of incoming messenges
					elif ( str(response).strip().startswith("From:") ):
						response = str(response) # Make sure response object is casted as a string
						response = response[5:] # Beautify the response string

						# don't print when the user logs in
						if response == str(ClientApp.user):
							pass
						else:
							response = str(response).replace(":", ": ") # Beautify the response string
							ClientApp.update_message_board(self, dt_string) # show the DT string in the incoming message frame
							ClientApp.update_message_board(self, response) # show the response in the incoming message frame
							time.sleep(1)
							pass

					elif ( str(response).strip().startswith("SIGNIN:") ):
							response = str(response).replace(":", ": ") # beautify string

							ClientApp.update_message_board(self, dt_string) # show the DT string in the incoming message frame
							ClientApp.update_message_board(self, response) # show the response in the incoming message frame
							self.ui.refresh_warning_label.show() # show the recommended refresh label
							time.sleep(1) # sleep for a sec brotha
							pass

					elif ( str(response).strip().startswith("SIGNOFF:") ):
							response = str(response).replace(":", ": ") # beautify string
							ClientApp.update_message_board(self, dt_string) # show the DT string in the incoming message frame
							ClientApp.update_message_board(self, response) # show the response in the incoming message frame
							self.ui.refresh_warning_label.show() # show the recommended refresh label
							time.sleep(1) # sleep for a sec my guy
							pass 

					else:
						ClientApp.update_message_board(self, dt_string) # show the DT string in the incoming message frame
						ClientApp.update_message_board(self, response) # show the response in the incoming message frame
						time.sleep(1)
						pass

				else:
					pass

		except Exception as e:
			if str(e).strip() == '[Errno 9] Bad file descriptor':
				pass
			else:
				print("\n\n Error occurred in listen_for_messages function. Error:")
				print(e)
		return

# end listen_for_incoming_messages

	def listen_for_new_users(self):

		try:
			list_users_string = 'LIST\n'
			ClientApp.client_socket.send(list_users_string.encode()) # pass the list users string to the sockey

		except Exception as e:
			if str(e).strip() == '[Errno 9] Bad file descriptor':
				pass
			else:
				print("\n\n Error occurred in listen_for_messages function. Error:")
				print(e)

		time.sleep(1)

		# Reformat the online users string
		ClientApp.online_users = str(ClientApp.online_users).strip()
		ClientApp.online_users = ClientApp.online_users.replace(",", "\n")
		self.ui.online_users.clear()
		self.ui.online_users.append(ClientApp.online_users)
		self.ui.online_users.repaint()

		ClientApp.refresh_warning_label_on = False # in the listening thread, this will hide the Recommend Refresh label

		return

# end listen_for_new_users

	def send_message(self):

		message_to = self.ui.sendTo.toPlainText() # Getting recipient from user
		message = self.ui.message_to_send.toPlainText() # Getting message from user

		send_message_string = "To:" + str(message_to).strip() + ":" + str(message) + "\n" # Prepping the string
		ClientApp.client_socket.send(send_message_string.encode()) # send the string to the client socket

		# Clear what was in the text boxes
		self.ui.sendTo.clear()
		self.ui.message_to_send.clear()
		self.ui.sendTo.repaint()
		self.ui.message_to_send.repaint()

		# Show your message in the message board
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

		ClientApp.update_outgoing_message_board(self, dt_string) # Append outgoing message board with DT string
		outgoing_message_board_update = "You : " + str(message_to).strip() + ": " + str(message) + "\n"
		ClientApp.update_outgoing_message_board(self, outgoing_message_board_update) # Append outgoing message board with outgoing message string

		return

# end send_message
	
	# Updates the message board
	def update_message_board(self, response):

		# sanity check
		if ":" in str(response):
			self.ui.messageBoard.append(response)
		return

# end update_message_board
	
	# Updates the outgoing message baord
	def update_outgoing_message_board(self, message):

		# sanity check
		self.ui.outgoing_messageBoard.append(message)
		self.ui.outgoing_messageBoard.repaint()
		return

# end update_outgoing_message_board

# end Class ClientApp

# (EOF)


