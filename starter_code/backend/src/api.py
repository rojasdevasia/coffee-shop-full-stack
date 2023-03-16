import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json , sys
from flask_cors import CORS,cross_origin

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

with app.app_context():
    db_drop_and_create_all()

# CORS(app,resources={r"/" : {'origins': '*'}})

#After_request decorator to set Access-Control-Allow
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
#     return response


# ROUTES
'''
@ implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# GET /drinks
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks=Drink.query.all()
        drinks_short=[drink.short() for drink in drinks]

        return jsonify({
            "success": True, 
            "drinks": drinks_short
        })
    except Exception as e:
        print(e)
        abort(404)    

'''
@implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
#GET /drinks-detail
@app.route('/drinks-detail',methods=['GET'])
# @requires_auth('get:drinks-detail')
def get_drinks_detail():
    try:
        drinks=Drink.query.all()
        drinks_long=[drink.long() for drink in drinks]

        return jsonify({
            "success": True, 
            "drinks": drinks_long
        })
    except Exception as e:
        print(e)
        abort(404)  

'''
@ implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
#POST /drinks
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
# @cross_origin()
def add_drinks(payload):
    body=request.get_json()
    try:
        title=body.get('title',None)
        recipe=body.get('recipe',None)
        drink=Drink(title=title,recipe=json.dumps(recipe))
        drink.insert()

        drinks=Drink.query.filter(Drink.id == drink.id).one_or_none()
        return jsonify({
            "success": True, 
            "drinks": [drinks.long()]
        })
    except Exception as e:
        print(e)
        abort(404)  

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload,id):
    try:
        drink=Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)
        else:
            body=request.get_json()
            title=body.get('title',None)
            recipe=body.get('recipe',None)
            
            drink.update(title=title,recipe=json.dumps(recipe))

        return jsonify({
            "success": True, 
            "drinks": Drink.query.all()
        })
    except Exception as e:
        print(e)
        abort(404) 

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload,id):
    try:
        drink=Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)
        else:
            drink.delete()

        return jsonify({
            "success": True, 
            "drinks": id
        })
    except Exception as e:
        print(e)
        abort(404) 

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(403)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden access"
    }), 403

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404

@app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "not allowed"
    }), 405

@app.errorhandler(AuthError)
def authorization_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code

# if __name__ == '__main__':
#   app.run(host='0.0.0.0', port=30006, debug=True)
