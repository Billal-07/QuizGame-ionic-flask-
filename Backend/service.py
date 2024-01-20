from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app)

app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/QuizGame'
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    existing_user = mongo.db.users.find_one({"username": data["username"]})
    if existing_user:
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    new_user = {
        "username": data["username"],
        "email": data["email"],
        "password": hashed_password,
        "contact_number" : data["contact_number"]
    }
    mongo.db.users.insert_one(new_user)

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = mongo.db.users.find_one({"username": data["username"]})

    if user and bcrypt.check_password_hash(user["password"], data["password"]):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()

    new_feedback = {
        "username": data["username"],
        "message": data["message"]
    }
    mongo.db.feedbacks.insert_one(new_feedback)

    return jsonify({"message": "Feedback submitted successfully"}), 201

@app.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    feedbacks = mongo.db.feedbacks.find({}, {'_id': 0})

    feedback_list = list(feedbacks)
    return jsonify({"feedbacks": feedback_list})


@app.route('/add_question', methods=['POST'])
def add_question():
    data = request.get_json()

    new_question = {
        "question_text": data["question_text"],
        "options": data["options"],
        "correct_option": data["correct_option"]
    }
    mongo.db.questions.insert_one(new_question)

    return jsonify({"message": "Question added successfully"}), 201

@app.route('/get_questions', methods=['GET'])
def get_questions():
    questions = mongo.db.questions.find({}, {'_id': 0})

    question_list = list(questions)
    return jsonify({"questions": question_list})

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    data = request.get_json()

    questions = mongo.db.questions.find({}, {'_id': 0})
    correct_answers = {str(q['correct_option']) for q in questions}

    user_answers = set(data.get("answers", []))
    score = len(correct_answers.intersection(user_answers))

    return jsonify({"score": score, "total_questions": len(correct_answers)}), 200


if __name__ == '__main__':
    app.run(debug=True)
