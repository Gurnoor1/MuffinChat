from tkinter import *
from functools import partial
import socket
import select
import errno
import time

HEADER_LENGTH = 10

IP = "10.130.40.199"
PORT = 5287

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)


# Code to add a username for the client
def validateLogin(username):
	myName = username.get()
	username = myName.encode('utf-8')
	username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
	client_socket.send(username_header + username)
	window.destroy()

# Making a function to easily insert text into the messagebox, only used in update()
def messageInsert(text):
	messageBox.config(state='normal')
	messageBox.insert(INSERT, text)
	messageBox.config(state='disabled')

def talk():
	message = userInput.get()
	messageInsert('Me >> ' + message + '\n')
	if message:
		# Encode message to bytes, prepare header and convert to bytes, like for username above, then send
		message = message + '\n'
		message = message.encode('utf-8')
		message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
		client_socket.send(message_header + message)


# dont touch dumbass it works dont question
def update():
	try:
		# loop over received messages (there might be more than one) and print them
		while True:
			# Receive our "header" containing username length, it's size is defined and constant
			username_header = client_socket.recv(HEADER_LENGTH)
			# If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
			if not len(username_header):
				print('Connection closed by the server')
				sys.exit()
			# Convert header to int value
			username_length = int(username_header.decode('utf-8').strip())
			# Receive and decode username
			username = client_socket.recv(username_length).decode('utf-8')
			# Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
			message_header = client_socket.recv(HEADER_LENGTH)
			message_length = int(message_header.decode('utf-8').strip())
			message = client_socket.recv(message_length).decode('utf-8')
			# Print message
			messageInsert(f'{username} >> {message}')
	except IOError as e:
		# This is normal on non blocking connections - when there are no incoming data error is going to be raised
		# Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
		# We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
		# If we got different error code - something happened
		if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
			print('Reading error: {}'.format(str(e)))
			sys.exit()
		# We just did not receive anything
		pass
	except Exception as e:
		# Any other exception - something happened, exit
		print('Reading error: '.format(str(e)))
		sys.exit()
	messageBox.after(1000, update)

# Login page

window = Tk()  

window.geometry('400x150')  
window.title('MuffinChat Login')

#username label and text entry box
usernameLabel = Label(window, text="Username: ").grid(row=0, column=0)
username = StringVar()
usernameEntry = Entry(window, textvariable=username).grid(row=0, column=1)  

validateLogin = partial(validateLogin, username)

#login button
loginButton = Button(window, text="Login", command=validateLogin).grid(row=4, column=0)  

window.mainloop()

# Main chat
# Basic setup
window = Tk()
window.geometry('800x300')
window.title('MuffinChat')

# Box to display messages
messageBox = Text(window, height=10, width=50)
messageBox.pack()
messageBox.after(500, update)

# Input box to send messages
userInput = StringVar()
messageEntry = Entry(window, textvariable=userInput)
messageEntry.pack()

# Button to send the message
sendButton = Button(window, text='send', command=talk)
sendButton.pack()

window.mainloop()