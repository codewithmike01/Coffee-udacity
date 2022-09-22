import os
from queue import Empty
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# Uncomment for first run
# db_drop_and_create_all()

# ROUTES

# Get all Drinks Short
@app.route('/drinks', methods=['GET'])
@requires_auth('get:drinks')
def get_drinks(jwt):
    drinks = Drink.query.all()

    if drinks is Empty:
        abort(404)
        
    drink_short = [ drink.short() for drink in drinks]
    

    return jsonify({
       "success":True,
       "drinks":drink_short 
    })



# Get Drink Details
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink(jwt):
    drinks = Drink.query.all()

  
    drink_long = [ drink.long() for drink in drinks]
    return jsonify({
        "success":True,
        "drinks": drink_long
    })


# Create Drink
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()
   
    if body is not None:
        new_title = body.get('title', None)
        new_recipe = json.dumps(body.get('recipe',None))
        drink = Drink( title = new_title, recipe = new_recipe)
        drink.insert()
        return jsonify({
            'success': True,
            "drinks": drink.long()
        })
    else:
         abort(404)


# Update Drinks
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    drink = Drink.query.get(id)
    body = request.get_json()

    if body is not None:
        new_title = body.get('title',None)
        new_recipe = body.get('recipe', None)

        if drink is None:
            abort(404)

        if new_title is not None:
            drink.title = new_title
    
        if new_recipe is not None:
            new_recipe = json.dumps(new_recipe)
            drink.recipe = new_recipe
    
        drinks = Drink.query.all()
        drink_short = [ drink.short() for drink in drinks]
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": drink_short
        })
    else:
        abort(404)

        
# Delete Drink
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('patch:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)
    
    drink.delete()
    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


# 404 Error
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404