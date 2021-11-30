import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****
SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678
flag = True

# HELPER SOCKET METHODS

def build_and_send_message(conn, code, data):
    """
	Builds a new message using chatlib, wanted code and message. 
	Prints debug info, then sends it to the given socket.
	Paramaters: conn (socket object), code (str), data (str)
	Returns: Nothing
	"""
    # Implement Code
    msg_protocol = chatlib.build_message(code, data)
    conn.send(msg_protocol.encode())


def recv_message_and_parse(conn):
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
    return code, msg



def build_send_recv_parse(conn, code, data):
    build_and_send_message(conn, code, data)
    msg_code, msg_data = recv_message_and_parse(conn)
    return msg_code, msg_data


def get_score(conn):
    msg_code, msg_data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["my_score"], '')
    return msg_code, msg_data


def get_high_score(conn):
    msg_code, msg_data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["high_score"], '')
    return msg_code, msg_data


def connect():
    # Implement Code
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((SERVER_IP, SERVER_PORT))

    return my_socket


def error_and_exit(error_msg):
    # Implement code
    print(error_msg)


def play_question(conn):
    global flag

    msg_code, msg_data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT['get_question'], '')
    if msg_code == chatlib.PROTOCOL_SERVER['no_questions']:
        print('You have been answered on all the trivia questions \n "GAME OVER"')
        print(msg_data)
        flag = False
    else:
        answer = input(msg_data.split('#')[1] + '?' + '\n1.\t' + msg_data.split('#')[2] +
                       '\n2.\t' + msg_data.split('#')[3] + '\n3.\t' + msg_data.split('#')[4] +
                       '\n4.\t' + msg_data.split('#')[5] +
                       '\nPlease choose an answer [1-4]:\n')
        msg_code, msg_data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT['send_answer'],
                                                   chatlib.join_data([msg_data.split('#')[0], answer]))
        if msg_code == chatlib.PROTOCOL_SERVER['correct_answer']:
            print(msg_code + ': The answer is "' + answer + '"\n')
        else:
            print(msg_code + ': ' + 'The answer is "' + msg_data + '"\n')


def get_logged_users(conn):
    msg_code, msg_data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT['logged'], '')
    print('Logged users:\n' + msg_data)


def login(conn):
    cmd = ''
    while cmd != chatlib.PROTOCOL_SERVER["login_ok_msg"]:
        username = input("Please enter username: \n")
        password = input('Please enter password: \n')
        # Implement code

        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], chatlib.join_data([username, password]))
        cmd, msg = recv_message_and_parse(conn)
        if cmd != chatlib.PROTOCOL_SERVER["login_ok_msg"]:
            error_and_exit(msg)

    print('\nLogged in!\n')
    # Implement code
    return


def logout(conn):
    # Implement code
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], '')


def main():
    # Implement code
    print('\nWelcome to Shmuel Safrin: " TRIVIA GAME "  \n')
    global flag
    conn = connect()
    login(conn)

    option = ''
    while option != 0:
        option = input('Please choose which action do you want to do: \n'
              'for Quit press 0 \n'
              'for check your score press 1 \n'
              'for check score of all participants press 2 \n'
              'for get a question to play press 3 \n'        
              'for get all current logged users press 4 \n')
        if option == '0':
            break
        elif option == '1':
            cmd, msg = get_score(conn)
            print(cmd + ' is: ' + msg + ' points')
        elif option == '2':
            cmd, msg = get_high_score(conn)
            print('\nHigh-Score table:')
            print(msg)
        elif option == '3':
            play_question(conn)
            if not flag:
                break
        elif option == '4':
            get_logged_users(conn)
        else:
            print("You chose invalid option")

    logout(conn)
    print("Goodbye!")
    conn.close()


if __name__ == '__main__':
    main()
