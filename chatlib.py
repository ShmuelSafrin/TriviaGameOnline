# Protocol Constants

CMD_FIELD_LENGTH = 16	# Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10**LENGTH_FIELD_LENGTH-1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages 
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
	"login_msg": "LOGIN",
	"logout_msg": "LOGOUT",
	# .. Add more commands if needed
	"my_score": "MY_SCORE",
	"high_score": "HIGH_SCORE",
	'get_question': 'GET_QUESTION',
	'send_answer': 'SEND_ANSWER',
	'logged': 'LOGGED'
}


PROTOCOL_SERVER = {
	"login_ok_msg": "LOGIN_OK",
	"login_failed_msg": "ERROR",
# ..  Add more commands if needed
	'your_score': 'YOUR_SCORE',
	'all_score': 'ALL_SCORE',
	'logged_answer': 'LOGGED_ANSWER',
	'your_question': 'YOUR_QUESTION',
	'correct_answer': 'CORRECT_ANSWER',
	'wrong_answer': 'WRONG_ANSWER',
	'no_questions': 'NO_QUESTIONS'
}


# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
	"""
	Gets command name (str) and data field (str) and creates a valid protocol message
	Returns: str, or None if error occured
	"""
# Implement code ...

	if (len(cmd) > CMD_FIELD_LENGTH) or (len(data) > MAX_DATA_LENGTH):
		return None

	while len(cmd) < CMD_FIELD_LENGTH:
		cmd += ' '

	field_length = str(len(data))
	while len(field_length) < LENGTH_FIELD_LENGTH:
		field_length = '0' + field_length

	return cmd + DELIMITER + field_length + DELIMITER + data


    #return full_msg


def parse_message(data):
	"""
	Parses protocol message and returns command name and data field
	Returns: cmd (str), data (str). If some error occured, returns None, None
	"""
# Implement code ...
	counter = 0
	for char in data:
		if char == '|':
			counter += 1
	if counter < 2:
		return None, None

	if data.split('|')[2] == '' and data.split('|')[1] == '0000':
		cmd = ''
		msg = ''
		for c in data.split('|')[0]:
			if c != ' ':
				cmd += c
		return cmd, msg

	length = data.split('|')[1].strip()
	if not(length.isdigit()):
		return None, None

	if int(length) != len(data.split('|')[2]):
		return None, None

	cmd = data.split('|')[0].strip()
	msg = data.split('|')[2]
# The function should return 2 values
	return cmd, msg

	
def split_data(msg, expected_fields):
	"""
	Helper method. gets a string and number of expected fields in it. Splits the string 
	using protocol's data field delimiter (|#) and validates that there are correct number of fields.
	Returns: list of fields if all ok. If some error occured, returns None
	"""
	# Implement code ...
	counter = 0
	for char in msg:
		if char == '#':
			counter = counter + 1
	if counter == expected_fields - 1:
		return msg.split('#')
	else:
		return [None]



def join_data(msg_fields):
	"""
	Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter. 
	Returns: string that looks like cell1#cell2#cell3
	"""
	# Implement code ...
	return '#'.join(msg_fields)