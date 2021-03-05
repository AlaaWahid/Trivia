from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


# Set up CORS. Allow '*' for origins. Delete the sample route
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


# Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

# Create an endpoint to handle GET requests for all available categories
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categ = {}
        for category in categories:
            categ[category.id] = category.type
        if len(categories) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': categ
        })

# handle GET requests for questions, including pagination (every 10 questions)
    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.all()
        categories = Category.query.all()
        curr_question = paginate_questions(request, selection)
        categ = {}
        for category in categories:
            categ[category.id] = category.type
        if len(curr_question) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': curr_question,
            'total_questions': len(selection),
            'current_category': None,
            'categories': categ
        })

# Create an endpoint to DELETE question using a question ID.
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if Question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            curr_questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': curr_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

# Create an endpoint to POST a new question
# Create a POST endpoint to get questions based on a search term.
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        search_term = body.get('searchTerm', None)
        try:
            if search_term:
                selection = Question.query.filter(
                    Question.question.ilike(f'%{search_term}%')).all()
                curr_questions = paginate_questions(request, selection)
                return jsonify({
                    'success': True,
                    'questions': curr_questions,
                    'total questions': len(selection)
                      })
            else:
                question = Question(question=new_question, answer=new_answer,
                                    category=new_category,
                                    difficulty=new_difficulty)
                question.insert()
                selection = Question.query.order_by(Question.id).all()
                curr_questions = paginate_questions(request, selection)
                return jsonify({
                   'success': True,
                   'created': question.id,
                   'questions': curr_questions,
                   'total questions': len(Question.query.all())
                      })
        except:
            abort(422)

# Create a GET endpoint to get questions based on category.
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_by_category(category_id):
        selection = Question.query.filter_by(category=category_id).all()
        curr_question = paginate_questions(request, selection)
        if len(curr_question) == 0:
            abort(404)
        categ = Category.query.filter_by(id=category_id).one_or_none()
        return jsonify({
            'success': True,
            'questions': curr_question,
            'current category': categ.type,
            'total question': len(selection)
        })

# Create a POST endpoint to get questions to play the quiz.
    @app.route('/quizzes', methods=['POST'])
    def get_questions_to_play_quiz():
        body = request.get_json()
        question_previous = body.get('previous_questions')
        category = body.get('quiz_category')
        if category['id'] == 0:
            quests = Question.query.all()
        else:
            quests = Question.query.filter(
                     Question.category == category['id']).all()
        quest = [question.format() for question in quests
                 if question.id not in question_previous]
        quest_random = random.choice(quest)
        return jsonify({
            "success": True,
            "question": quest_random
        })
# Create error handlers for all expected errors including 404 and 422.

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def uprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405
    return app
