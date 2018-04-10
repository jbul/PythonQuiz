import os
import datetime
import copy
import config
import random
import string
from flask import Flask, request, send_from_directory, render_template, jsonify, json, session

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

# Utils methods
# Returns the current date in string
def get_current_date():
    return datetime.datetime.now().strftime("%d/%m/%y %I:%M%p")


# Saves the given result in the save.json file
def save_results(path, data_to_save=None):
    SITE_ROOT = os.path.realpath(os.path.dirname(path))
    json_url = os.path.join(SITE_ROOT, "static/data", "save.json")
    data = {}
    data_file = None
    if os.path.exists(json_url):
        data_file = open(json_url)
        data = json.load(data_file)
        data_file.close()

    if not type(data) is dict:
        data.append(data_to_save)
    else:
        data = [data_to_save]
        # w+ used to create file if not existing
    data_file = open(json_url, "w+")
    data_file.write(json.dumps(data))


# Returns the data contained in the given file
def get_data_in_file(path, filename):
    SITE_ROOT = os.path.realpath(os.path.dirname(path))
    json_url = os.path.join(SITE_ROOT, "static/data", filename)
    data = json.load(open(json_url))
    return data


# Returns all the quiz array format
def get_all_quiz(path):
    return get_data_in_file(path, "quiz.json")["quiz_list"]


# Get data inside the quiz at given index
def get_quiz_data(path, quiz_index):
    return get_all_quiz(path)[quiz_index]


# Returns a dictionary containing the title and its position in the quiz array
def get_quiz_title_number(path):
    data = get_all_quiz(path)
    result = {}
    index = 0
    for quiz in data:
        result[index] = quiz["title"]
        index = index + 1
    return result


# Gets the list of quiz that have been proposed (follows pattern save-USERNAME.json)
def get_quiz_propositions(path):
    result = []
    SITE_ROOT = os.path.realpath(os.path.dirname(path))
    for filename in os.listdir(os.path.join(SITE_ROOT, "static/data/")):
        if 'save-' in filename:
            result.append(get_data_in_file(path, filename))
    return result


# Calculates quiz results and returns a dictionary with the quiz title and result
def get_quiz_result(data_path=None, quiz=None):
    result = {}
    if quiz and data_path:
        data_quiz = get_quiz_data(data_path, int(quiz["quiz_index"]))
        result["quiz_title"] = data_quiz["title"]
        result["quiz_result"] = {}
        idx = 0
        good_answer = 0
        bad_answer = 0
        for key in data_quiz["questions"]:
            is_correct = quiz[key["title"]] == key["choices"][key["answer"]]
            result["quiz_result"][idx] = {
                "title" : key["title"],
                "result" : is_correct,
                "expected" :  key["choices"][key["answer"]],
                "given" : quiz[key["title"]]
            }
            if is_correct:
                good_answer = good_answer + 1
            else:
                bad_answer = bad_answer + 1
            idx = idx + 1

        result["overall"] = { "good_answer" : good_answer,
                              "bad_answer" : bad_answer,
                              "total" : int((float(good_answer) / float(idx)) * 100)
                            }
    return result


# Transform data from the form into a dictionary and saves it in a file
def saveQuizInformation(path, quizInfo=None):
    result = {}
    if quizInfo:
        result["username"] = quizInfo["username"]
        result["title"] = quizInfo["quizTitle"]
        result["questions"] = []
        result["added_date"] = get_current_date()

        quizLength = len(quizInfo)
        for idx in range(0, ((quizLength - 2)) // 5) :
            entry = {}
            entry["title"] = quizInfo["question-title-{0}".format(idx)]
            entry["choices"] = [
                                quizInfo["question-choice-1-{0}".format(idx)],
                                quizInfo["question-choice-2-{0}".format(idx)],
                                quizInfo["question-choice-3-{0}".format(idx)],
                                quizInfo["question-choice-4-{0}".format(idx)]
                                ]
            entry["answer"] = int(quizInfo["question-answer-{0}".format(idx)])
            result["questions"].append(entry)

        SITE_ROOT = os.path.realpath(os.path.dirname(path))
        json_url = os.path.join(SITE_ROOT, "static/data", "save-{0}.json".format(result["username"]))
        outputFile = open(json_url, "w+")
        outputFile.write(json.dumps(result))
    return 1


# Removes file from static/data directory (HARD DELETE)
def delete_file(path, filename):
    SITE_ROOT = os.path.realpath(os.path.dirname(path))
    json_url = os.path.join(SITE_ROOT, "static/data", filename)
    os.remove(json_url)


# Gets data in the file and add it into the quiz dictionary
def save_quiz(quizname):
    data_to_save = get_data_in_file(__file__, "save-{0}.json".format(quizname["quizUsername"]))
    data = get_data_in_file(__file__, "quiz.json")
    data["quiz_list"].append(data_to_save)
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", 'quiz.json')
    outputFile = open(json_url, "w+")
    outputFile.write(json.dumps(data))
    delete_file(__file__, "save-{0}.json".format(quizname["quizUsername"]))


# Routings
# Main route
@app.route('/')
def root():
    data = get_quiz_title_number(__file__)
    return render_template('index.html', quiz_list=data)

# Quiz page route
@app.route('/quiz', methods = ["POST"])
def quiz():
    index = int(request.form["quiz"])
    quiz = get_quiz_data(__file__, index)
    return render_template('quiz.html', questions= quiz["questions"], title= quiz["title"], quiz_index=index )


# Validate quiz and display result page route with user result
@app.route('/quizChallenge', methods = ["POST"])
def quizChallenge():
    result = get_quiz_result(__file__, request.form)
    result["user"] = request.form["username"]
    result["date"] = get_current_date()
    save_results(__file__, result)
    return render_template("quiz_result.html", result = result)


# Display all results page, gets all results fron save.json and send it to page
@app.route('/seeAllResults', methods = ['GET'])
def seeAllResults():
    result = get_data_in_file(__file__, "save.json")
    return render_template("results.html", result = result)


# Display create quiz page
@app.route('/createQuiz', methods = ['GET'])
def createQuiz():
    return render_template("createQuiz.html")

# save a quiz for later validation / add
@app.route('/submitQuiz', methods = ['POST'])
def submitQuiz():
    saveQuizInformation(__file__, request.form)
    return render_template("quiz_submitted.html")

# login as admin
@app.route('/login', methods = ['POST', 'GET'])
def login():
    username = ""
    password = ""
    error = False

    if request.form:
        username = request.form["username"]
        password = request.form["password"]

    if not 'logged' in session:
        if request.form:
            if config.SESSION_LOGIN == username and config.SESSION_PWD == password:
                return render_template("validate_quiz.html", propositions = get_quiz_propositions(__file__), logged = True)
            else:
                error = True
    else:
        return render_template("validate_quiz.html", propositions = get_quiz_propositions(__file__))

    return render_template("login.html", error = error)


# Add chosen quiz in the main quiz directory
@app.route('/saveQuiz', methods = ['POST'])
def saveQuiz():
    save_quiz(request.form)
    data = get_quiz_title_number(__file__)
    return render_template("index.html", quiz_list = data)


if __name__ == "__main__":
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "quiz.json")
    app.run()
