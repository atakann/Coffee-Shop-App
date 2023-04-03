import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


#db_drop_and_create_all()


@app.route("/drinks", methods=["GET"])
def get_drinks():
    """
    GET /drinks
    Public endpoint
    Should contain only the drink.short() data representation
    Returns:
        - Status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks,
        - Appropriate status code indicating reason for failure.
    """
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({"success": True, "drinks": formatted_drinks}), 200


@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail(payload):
    """
    GET /drinks-detail
    Requires 'get:drinks-detail' permission
    Should contain the drink.long() data representation
    Returns:
        - Status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks,
        - Appropriate status code indicating reason for failure.
    """
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({"success": True, "drinks": formatted_drinks}), 200


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink(payload):
    """
    POST /drinks
    Requires 'post:drinks' permission
    Should create a new row in the drinks table
    Should contain the drink.long() data representation
    Returns:
        - Status code 200 and json {"success": True, "drinks": drink} where drink is an array containing only the newly created drink,
        - Appropriate status code indicating reason for failure.
    """
    body = request.get_json()

    title = body.get("title", None)
    recipe = body.get("recipe", None)

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        return jsonify({"success": True, "drinks": [drink.long()]}), 200
    except Exception as e:
        print(e)
        abort(422)


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(payload, id):
    """
    PATCH /drinks/<id>
    Requires 'patch:drinks' permission
    Should update the corresponding row for <id>
    Should contain the drink.long() data representation
    Returns:
        - Status code 200 and json {"success": True, "drinks": drink} where drink is an array containing only the updated drink,
        - 404 error if <id> is not found,
        - Appropriate status code indicating reason for failure.
    """
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    body = request.get_json()

    title = body.get("title", None)
    recipe = body.get("recipe", None)

    try:
        if title:
            drink.title = title
        if recipe:
            drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({"success": True, "drinks": [drink.long()]}), 200
    except Exception as e:
        print(e)
        abort(422)


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    """
    DELETE /drinks/<id>
    Requires 'delete:drinks' permission
    Should delete the corresponding row for <id>
    Returns:
        - Status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record,
        - 404 error if <id> is not found,
        - Appropriate status code indicating reason for failure.
    """
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.delete()
        return jsonify({"success": True, "delete": id}), 200
    except Exception as e:
        print(e)
        abort(422)


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )


@app.errorhandler(AuthError)
def handle_auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response
