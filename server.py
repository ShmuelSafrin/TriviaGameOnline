##############################################################################
# server.py
##############################################################################
import random
import socket
import chatlib
import select
import ast
import requests
import json
# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
messages_to_send = []  # contains tuples of (client_socket, massage)


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

    # conn.send(msg_protocol.encode())
    messages_to_send.append((conn, msg_protocol))
    print("[SERVER] " + str(conn.getpeername()) + " msg:\t", msg_protocol)  # Debug print


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
    print('[CLIENT] ' + str(conn.getpeername()) + ' msg:\t', full_msg)  # Debug print
    return code, msg


def create_random_question(username):
    global questions
    global users

    questions_asked = users[username]['questions_asked']
    id_questions = []
    keys = questions.keys()
    for k in keys:
        id_questions.append(k)
    for q in questions_asked:
        id_questions.remove(q)
    if id_questions == []:
        return None
    r = random.choice(id_questions)
    users[username]['questions_asked'].append(r)
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


def handle_question_message(conn, username):
    global users
    score_dict = {}
    your_question = create_random_question(username)
    if your_question == None:

        for user in users:
            score_dict[user] = users[user]['score']
        # score_dict = {'test': 0, 'yossi': 50, 'master': 200}
        high_score_string = descending_sorted_dict_to_string(score_dict)
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER['no_questions'], high_score_string)
        users[username]["score"] = 0
        users[username]["questions_asked"].clear()
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER['your_question'], your_question)


def handle_answer_message(conn, user_name, data):  # data = id#chice
    # 2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2}
    global questions
    global users
    id = int(data.split('#')[0])
    choice = int(data.split('#')[1])
    checking_answer = questions[id]['correct']
    if checking_answer == choice:
        # "test"		:	{"password": "test", "score": 0, "questions_asked": []}
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
    # importing the module


    # reading the data from the file
    with open('questions.txt') as f:
        questions = f.read()
    questions = ast.literal_eval(questions)


    #questions = {
     #   2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2},
      #  4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
       #        "correct": 3}
     #}
    return questions


def load_questions_from_web():
    # all sort of trivia's questions
    #response = requests.get("https://opentdb.com/api.php?amount=50&type=multiple")#
    #  computer science trivia's questions
    response = requests.get("https://opentdb.com/api.php?amount=50&category=18&type=multiple")
    response_data = response.json()
    list_of_dicts = response_data['results']
    questions = {}
    question = {}
    i = 0
    for d in list_of_dicts:
        i += 1
        question['question'] = d['question']
        r = random.randint(0, 3)  # include 3
        list_answers = d['incorrect_answers']
        list_answers.insert(r, d['correct_answer'])
        question['answers'] = list_answers
        question['correct'] = r + 1
        questions[i] = dict(question)

    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    with open('users.txt') as f:
        users = f.read()
    users = json.loads(users)
    f.close()
    #users = {
     #   "test": {"password": "test", "score": 0, "questions_asked": []},
      #  "yossi": {"password": "123", "score": 50, "questions_asked": []},
       # "master": {"password": "master", "score": 200, "questions_asked": []}}
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


def descending_sorted_dict_to_string(dict):
    keys = dict.keys()
    values = dict.values()
    list_keys = []
    list_values = []

    for k in keys:
        list_keys.append(k)
    for v in values:
        list_values.append(v)

    length = len(dict) - 1
    for i in range(length, 0, -1):
        for j in range(0, i):
            if list_values[j] < list_values[j + 1]:
                tempKey = list_keys[j]
                list_keys[j] = list_keys[j + 1]
                list_keys[j + 1] = tempKey
                tempvalue = list_values[j]
                list_values[j] = list_values[j + 1]
                list_values[j + 1] = tempvalue
    string = ''
    for i in range(len(list_keys)):
        string += list_keys[i] + ': ' + str(list_values[i]) + '\n'
    return string


def handle_high_score_message(conn):
    global users
    score_dict = {}
    for user in users:
        score_dict[user] = users[user]['score']
    # score_dict = {'test': 0, 'yossi': 50, 'master': 200}
    high_score_string = descending_sorted_dict_to_string(score_dict)
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER['all_score'], high_score_string)


def handle_logged_message(conn):
    global users
    global logged_users

    #users = load_user_database()
    #users_connect = ''
    #for user in users:
       #users_connect += user
       #users_connect += ','
    logged_names = ''
    for log_name in logged_users.values():
        logged_names += log_name + ','

    build_and_send_message(conn, chatlib.PROTOCOL_SERVER['logged_answer'], logged_names)


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users

    # Implement code ...
    logged_users.pop(conn.getpeername())
    print("Connection closed", conn.getpeername())
    conn.close()



def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users  # To be used later

    # Implement code ...
    user_name = data.split('#')[0]
    password = data.split('#')[1]
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
    global logged_users  # To be used later

    # Implement code ...
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
        username = logged_users[conn.getpeername()]
        handle_question_message(conn, username)
    elif cmd == chatlib.PROTOCOL_CLIENT['send_answer']:
        user_name = logged_users[conn.getpeername()]
        handle_answer_message(conn, user_name, data)  # data = id#chice


def print_client_sockets(client_sockets):
    for c in client_sockets:
        print("\t", c.getpeername())
    print('\n')


def main():
    # Initializes global users and questions dicionaries using load functions, will be used later
    global users
    global questions
    global messages_to_send
    global logged_users
    client_sockets = []
    users = load_user_database()
    #questions = load_questions()
    questions = load_questions_from_web()
    print("Welcome to Trivia Server!")

    # Implement code ...
    server_socket = setup_socket()
    print("Listening for clients...")
    while True:
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                (client_socket, client_address) = current_socket.accept()
                print("New client joined!", client_address)
                client_sockets.append(client_socket)
                print('\nThe clients who are joined')
                print_client_sockets(client_sockets)
            else:
                print("New data from client...")
                try:
                    #data = current_socket.recv(MAX_MSG_LENGTH).decode()
                    code, msg = recv_message_and_parse(current_socket)
                except:
                    print("Connection closed", current_socket.getpeername())
                    client_sockets.remove(current_socket)
                    if current_socket.getpeername() in logged_users:
                        logged_users.pop(current_socket.getpeername())
                    current_socket.close()
                    print('The logged clients who left are: ' + str(logged_users))
                    break
                if code == chatlib.PROTOCOL_CLIENT['logout_msg']:
                    client_sockets.remove(current_socket)
                    handle_client_message(current_socket, code, msg)
                    print_client_sockets(client_sockets)
                else:
                    handle_client_message(current_socket, code, msg)
                    if code == chatlib.PROTOCOL_CLIENT['login_msg']:
                        print('The logged users: ' + str(logged_users) + '\n')
                    for message in messages_to_send:
                        current_socket, data = message
                        if current_socket in ready_to_write:
                            current_socket.send(data.encode())
                            messages_to_send.remove(message)


if __name__ == '__main__':
    main()
