import json

from auth.auth import requires_auth, AuthError
from database.models import db_drop_and_create_all, setup_db, Drink
from flask import Flask, jsonify, abort
from flask import request
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES
'''
@TASK implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    return jsonify({
        "success": True,
        "drinks": [d.short() for d in Drink.query.all()]
    })


'''
@TASK implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth("get:drinks-detail")
def drinks_detail(token_payload):
    return jsonify({
        "success": True,
        "drinks": [d.long() for d in Drink.query.all()]
    })


'''
@TASK implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly 
    created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(token_payload):
    payload = request.get_json()
    new_drink = Drink(title=payload['title'], recipe=json.dumps(payload['recipe']))
    new_drink.insert()
    return jsonify({"success": True, "drinks": [new_drink.long()]})


'''
@TASK implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token_payload, id):
    payload = request.get_json()
    drink_for_patch = Drink.query.filter(Drink.id == id).one_or_none()
    if drink_for_patch != None:
        drink_for_patch.title = payload.get('title')
        if payload.get('recipe'):
            drink_for_patch.recipe = json.dumps(payload.get('recipe'))
        drink_for_patch.update()
        return jsonify({"success": True, "drinks": drink_for_patch.long()})
    abort(404)


'''
@TASK implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink_for_delete = Drink.query.filter(Drink.id == id).one_or_none()
    if drink_for_delete != None:
        drink_for_delete.delete()
        return jsonify({"success": True, "delete": drink_for_delete.id})
    abort(404)


## Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(IntegrityError)
def integrity_error(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "check your data, some unique constrains is violated"
    }), 400


@app.errorhandler(AuthError)
def auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error['description']
    }), ex.status_code


if __name__ == '__main__':
    app.run()
