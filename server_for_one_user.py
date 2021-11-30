##############################################################################
# server_for_one_user.py
##############################################################################
import random
import socket
import chatlib
import select
import operator
import client
# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
messages_to_send = []  # contains tuples of (client, massage)
client_sockets = []
ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"
MAX_MSG_LENGTH = 1024

# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
	global messages_to_send
	## copy from client
	"""
		Builds a new message using chatlib, wanted code and message.
		Prints debug info, then sends it to the given socket.
		Paramaters: conn (socket object), code (str), data (str)
		Returns: Nothing
		"""
	# Implement Code
	msg_protocol = chatlib.build_message(code, msg)

	conn.send(msg_protocol.encode())
	print("[SERVER] " + str(conn.getpeername()) + " msg:\t", msg_protocol)	  # Debug print

def recv_message_and_parse(conn):
	## copy from client

	""""
       Recieves a new message from given socket,
       then parses the message using chatlib.
       Paramaters: conn (socket object)
       Returns: cmd (str) and data (str) of the received message.
       If error occured, will return None, None
       """
	# Implement Code

	full_msg = conn.recv(1024).decode()
	code, msg = chatlib.parse_message(full_msg)
	print('[CLIENT] ' + str(conn.getpeername()) + ' msg:\t', full_msg)	  # Debug print
	return code, msg


def create_random_question():
	global questions

	questions = load_questions()
	keys = questions.keys()
	id_questions = list()
	for k in keys:
		id_questions.append(k)
	r = random.choice(id_questions)
	your_question = str()
	question = questions[r]['question']
	answers = questions[r]['answers']
	answers = ' '.join(answers)
	answers = answers.replace(' ', '#')
	your_question += str(r) + '#'
	your_question += question + '#'
	your_question += answers
	#   your_question = "id#question#answer1#answer2#answer3#answer4"
	return your_question


def handle_question_message(conn):
	your_question = create_random_question()
	build_and_send_message(conn, chatlib.PROTOCOL_SERVER['your_question'], your_question)

def handle_answer_message(conn, user_name, data): # data = id#chice
	#2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2}
	global questions
	global users
	id = int(data.split('#')[0])
	choice = int(data.split('#')[1])
	questions = load_questions()
	checking_answer = questions[id]['correct']
	if checking_answer == choice:
		#"test"		:	{"password": "test", "score": 0, "questions_asked": []}
		users[user_name]["score"] += 5
		build_and_send_message(conn, chatlib.PROTOCOL_SERVER['correct_answer'], '')
	else:
		build_and_send_message(conn, chatlib.PROTOCOL_SERVER['wrong_answer'], str(checking_answer))

# Data Loaders #

def load_questions():
	"""
	Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
	Recieves: -
	Returns: questions dictionary
	"""
	questions = {
				2313 : {"question":"How much is 2+2","answers":["3","4","2","1"],"correct":2},
				4122 : {"question":"What is the capital of France?","answers":["Lion","Marseille","Paris","Montpellier"],"correct":3} 
				}
	
	return questions

def load_user_database():
	"""
	Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
	Recieves: -
	Returns: user dictionary
	"""
	users = {
			"test"		:	{"password": "test", "score": 0, "questions_asked": []},
			"yossi"		:	{"password": "123", "score": 50, "questions_asked": []},
			"master"	:	{"password": "master", "score": 200, "questions_asked": []}
			}
	return users

	
# SOCKET CREATOR

def setup_socket():
	"""
	Creates new listening socket and returns it
	Recieves: -
	Returns: the socket object
	"""
	# Implement code ...

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((SERVER_IP, SERVER_PORT))
	server_socket.listen()
	return server_socket
	

def send_error(conn, error_msg):
	"""
	Send error message with given message
	Recieves: socket, message error string from called function
	Returns: None
	"""
	# Implement code ...

	build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], ERROR_MSG + error_msg)



	
##### MESSAGE HANDLING


def handle_getscore_message(conn, username):
	global users
	# Implement this in later chapters
	user_score = str(users[username]['score'])
	build_and_send_message(conn, chatlib.PROTOCOL_SERVER['your_score'], user_score)


def handle_high_score_message(conn):
	global users

	high_score_dict = {}
	for user in users:
		high_score_dict[user] = users[user]['score']
#high_score_dict ==  {'test': 0, 'yossi': 50, 'master': 200}
	sorted_high_score_dict = str(sorted(high_score_dict.items(), key=operator.itemgetter(1), reverse=True))
#sorted_high_score_dict = [('master', 200), ('yossi', 50), ('test', 0)]
# אני צריך לבדוק איך להחזיר סטרינג ובשורות נפרדות
	build_and_send_message(conn, chatlib.PROTOCOL_SERVER['all_score'], sorted_high_score_dict)


def handle_logged_message(conn):
	global users
	users = load_user_database()
	users_connect = ''
	for user in users:
		users_connect += user
		users_connect += ','
	build_and_send_message(conn, chatlib.PROTOCOL_SERVER['logged_answer'], users_connect)
	
def handle_logout_message(conn):
	"""
	Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
	Recieves: socket
	Returns: None
	"""
	global logged_users


	# Implement code ...
	logged_users.pop(conn.getpeername())
	conn.close()



def handle_login_message(conn, data):
	"""
	Gets socket and message data of login message. Checks  user and pass exists and match.
	If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
	Recieves: socket, message code and data
	Returns: None (sends answer to client)
	"""
	global users  # This is needed to access the same users dictionary from all functions
	global logged_users	 # To be used later
	
	# Implement code ...
	user_name = data.split('#')[0]
	password = data.split('#')[1]
	users = load_user_database()
	for user in users:
		if user == user_name:
			if users[user]['password'] == password:
				logged_users[conn.getpeername()] = user_name
				build_and_send_message(conn, chatlib.PROTOCOL_SERVER['login_ok_msg'], '')
				return
			else:
				send_error(conn, 'Password does not match!')
				return
	send_error(conn, 'Username does not exist')



def handle_client_message(conn, cmd, data):
	"""
	Gets message code and data and calls the right function to handle command
	Recieves: socket, message code and data
	Returns: None
	"""
	global logged_users	 # To be used later
	
	# Implement code ...
	#if conn.getpeername() not in logged_users:
	if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
		handle_login_message(conn, data)
	elif cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
		handle_logout_message(conn)
	elif cmd == chatlib.PROTOCOL_CLIENT["my_score"]:
		username = logged_users[conn.getpeername()]
		handle_getscore_message(conn, username)
	elif cmd == chatlib.PROTOCOL_CLIENT["high_score"]:
		handle_high_score_message(conn)
	elif cmd == chatlib.PROTOCOL_CLIENT['logged']:
		handle_logged_message(conn)
	elif cmd == chatlib.PROTOCOL_CLIENT['get_question']:
		handle_question_message(conn)
	elif cmd == chatlib.PROTOCOL_CLIENT['send_answer']:
		user_name = logged_users[conn.getpeername()]
		handle_answer_message(conn, user_name, data)  # data = id#chice


def main():
	# Initializes global users and questions dicionaries using load functions, will be used later
	global users
	global questions

	print("Welcome to Trivia Server!")

	# Implement code ...
	server_socket = setup_socket()
	print("Listening for clients...")
	while True:
		(client_socket, client_address) = server_socket.accept()
		print('New client joined! \t', client_socket.getpeername())
		while True:
			try:
				code, msg = recv_message_and_parse(client_socket)
			except:
				logged_users.pop(client_socket.getpeername())
				client.error_and_exit('The client abruptly was disconnect')
				break
			handle_client_message(client_socket, code, msg)
			if code == chatlib.PROTOCOL_CLIENT['logout_msg']:
				break


if __name__ == '__main__':
	main()

	