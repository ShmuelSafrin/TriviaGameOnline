import requests
import json
import random
response = requests.get("https://opentdb.com/browse.php?query=Science%3A+Computers&type=Category#/api.php?amount=50&type=multiple")
#response = requests.get("https://opentdb.com/api.php?amount=50&category=18&type=multiple")
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

print(questions)



#print(response_data['results'])
#print(type(response_data['results']))
#response = requests.get('http://randomfox.ca/floof')
#print(response.status_code)
#print(response.text)
#print(response.json())
#fox = response.json()
#print(fox['image'])
""""
 4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
       # "correct": 3}
{"category":"Entertainment: Music","type":"multiple","difficulty":"medium",
 "question":"Who is the founder and leader of industrial rock band, &#039;Nine Inch Nails&#039;?",
 "correct_answer":"Trent Reznor","incorrect_answers":["Marilyn Manson","Robin Finck","Josh Homme"]},
{"category":"Entertainment: Books","type":"multiple","difficulty":"hard",
  "question":"In the Beatrix Potter books, what type of animal is Tommy Brock?",
  "correct_answer":"Badger","incorrect_answers":["Fox","Frog","Rabbit"]}"
questions =
"""
