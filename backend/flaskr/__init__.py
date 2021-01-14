import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

os.sys.path.append('..')

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
ALL_CATEGORIES = 0

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  

  CORS(app, resources='*')
  

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = {}
    for category in Category.query.all():
      categories[category.id] = category.type

    return jsonify({'categories' : categories})


  @app.route('/questions', methods=['GET'])
  def get_paginated_questions():
    page = request.args.get('page', 1, type=int)
    current_category = request.args.get('category', ALL_CATEGORIES, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    if(current_category == ALL_CATEGORIES) : questions = Question.query.all()
    else :  questions = Question.query.filter(Question.category == str(current_category)).all()
    categories = Category.query.all()
    formatted_questions = [question.format() for question in questions]
    formatted_categories = {}
    for category in categories:
      formatted_categories[category.id] = category.type
    if len(questions[start:end]) == 0 or (current_category not in formatted_categories.keys() and current_category): 
      abort(404)
    
    return jsonify({'questions': formatted_questions[start:end], 
                    'total_questions': len(formatted_questions),
                    'categories': formatted_categories,
                    'current_category': current_category})


  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).first()
    if question == None:
      abort(404)
    question.delete()
    return jsonify({'success': True})



  @app.route('/questions/new', methods=['POST'])
  def create_new_question():
    data = request.json
    try:
      question = Question(data['question'], data['answer'], data['category'], data['difficulty'])
      question.insert()
      return jsonify({'success': True})
    except:
      abort(422)


  @app.route('/questions/search', methods=['POST'])
  def get_question_with_search():
    search_term = request.json['searchTerm']
    questions = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
    formatted_questions = [question.format() for question in questions]
    return jsonify({'questions': formatted_questions,
                    'total_questions': len(formatted_questions),
                    'current_category': ALL_CATEGORIES})


  @app.route('/categories/<category_id>/questions', methods=['GET'])
  def get_question_with_category(category_id):
    questions = Question.query.filter(Question.category == str(category_id)).all()
    if len(questions) == 0 :
      abort(404)
    formatted_questions = [question.format() for question in questions]
    return jsonify({'questions': formatted_questions,
                    'total_questions': len(formatted_questions),
                    'current_category': category_id})


  @app.route('/quizzes', methods=['POST'])
  def play_trivia():
    data = request.json
    category = data['quiz_category']
    previous_questions = data['previous_questions']
    if(category['id'] == ALL_CATEGORIES) :
      category_questions = Question.query.all()
    else : 
      category_questions = Question.query.filter(Question.category == str(category['id'])).all()

    if len(category_questions) == 0 : 
      abort(404)
    
    if(len(category_questions) == len(previous_questions)) :
      return jsonify({'question': None})
    
    while(1):
      next_question = random.choice(category_questions)
      if(next_question.id not in previous_questions) :
        break
    
    return jsonify({'question': next_question.format()})
    

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resource not found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    })

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    })

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method not allowed'
    })
  
  return app

if __name__ == "__main__":
  create_app().run()
    

    