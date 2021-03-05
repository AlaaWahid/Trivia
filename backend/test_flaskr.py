import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'postgres', '12345', 'localhost:5432', "trivia_test")
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Who is the best player?',
            'answer': 'Ronaldo',
            'category': 6,
            'difficulty': 2
        }
        self.new_quiz = {
            "previous_questions": [],
            "quiz_category":
            {
                "type": "Sports",
                "id": "6"
            }
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

# test for successful operation and for expected errors.

# Categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(['categories'])
        self.assertTrue(len(data['categories']))

# Questions--------------------------------
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(['questions'])
        self.assertTrue(len(data['questions']))

    def test_get_questions_fail(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

# Delete question----------------------------------------------

    def test_delete_question(self):
        res = self.client().delete('/questions/174')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 174)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# add question --------------------------------------------------------

    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))

    def test_add_question_fail(self):
        res = self.client().post('/questions/1000', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

# search ---------------------------------------------------------------------

    def test_search_question(self):
        res = self.client().post('/questions', json={'searchTerm': 'who'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total questions'])
        self.assertTrue(len(data['questions']))

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions', json={"searchTerm": "apple"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(len(data['questions']))

# get_question_by_category --------------------------------------------

    def test_get_question_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(['questions'])
        self.assertTrue(len(data['questions']))

    def test_get_question_by_category_fail(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

# quizzes ------------------------------------------------

    def test_get_questions_to_play_quiz(self):
        res = self.client().post('/quizzes', json=self.new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['question']))
        self.assertTrue(len(data['question']))

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
