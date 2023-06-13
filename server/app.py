import json, uuid, logging
from flask import Flask, request, jsonify, Response

logger = logging.Logger(__name__)

app = Flask(__name__)

import config

with open("pizza_types.json","r") as f:
    pizza_types = json.loads(f.read())

open_carts = {}

def get_cart(uid, key):
    if uid == None or key == None:
        return None
    if uid not in open_carts:
        return None
    if open_carts[uid]["key"] != key:
        return None
    return open_carts[uid]

@app.route("/")
def hello_world():
    # Return OK message
    return "{\"status\":200, \"message\": \"ok\"}", 200

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    # Return pizza types
    return jsonify(pizza_types), 200

@app.route("/cart/open", methods=["POST"])
def open_cart():
    # Generate cart id and ensure it is unique
    foundunique = False
    while not foundunique:
        cart_id = str(uuid.uuid4())
        if cart_id in open_carts:
            logger.warn("Regenerating UUID for new cart - prev " + cart_id)
        else:
            foundunique = True
    cart_key = str(uuid.uuid4())
    # Append cart to list of open carts
    open_carts[cart_id] = {
        "key": cart_key,
        "items": []
    }
    logger.debug("Cart created with ID " + cart_id + " and key " + cart_key)
    return "{\"status\":200, \"id\": \"" + cart_id + "\", \"key\": \"" + cart_key + "\"}", 200

@app.route("/cart/items", methods=["GET"])
def get_cart_items():
    # Get cart id and key from request
    cart_id = request.args.get("id")
    cart_key = request.args.get("key")
    # Get cart and verify not none
    cart = get_cart(cart_id, cart_key)
    if cart == None:
        return "{\"status\":403, \"message\": \"invalid cart credentials\"}", 403
    return "{\"status\":200, \"items\": " + json.dumps(cart["items"]) + "}", 200

@app.route("/cart/add", methods=["POST"])
def add_cart_item():
    # Get cart id and key from request
    cart_id = request.args.get("id")
    cart_key = request.args.get("key")
    # Get cart and verify not none
    cart = get_cart(cart_id, cart_key)
    if cart == None:
        return "{\"status\":403, \"message\": \"invalid cart credentials\"}", 403
    # Get pizza type from request
    pizza_type = request.args.get("type")
    if pizza_type == None:
        return "{\"status\":400, \"message\": \"missing pizza type\"}", 400
    # Get pizza type from pizza types
    pizza_type_obj = None
    for type in pizza_types:
        if type["id"] == pizza_type:
            pizza_type_obj = type
            break
    if pizza_type_obj == None:
        return "{\"status\":400, \"message\": \"invalid pizza type\"}", 400
    # Get number of people from request
    num_people = request.args.get("num_people")
    if num_people == None:
        return "{\"status\":400, \"message\": \"missing number of people\"}", 400
    # Test for invalid number of people and convert to integer
    try:
        num_people = int(num_people)
    except:
        return "{\"status\":400, \"message\": \"invalid number of people\"}", 400
    # Get stuffed crust from request
    stuffed_crust = request.args.get("stuffed_crust")
    if stuffed_crust == None:
        return "{\"status\":400, \"message\": \"missing stuffed crust\"}", 400
    # Test for invalid stuffed crust and convert to boolean
    if stuffed_crust == "true":
        stuffed_crust = True
    elif stuffed_crust == "false":
        stuffed_crust = False
    else:
        return "{\"status\":400, \"message\": \"invalid stuffed crust\"}", 400
    cart["items"].append({
        "type": pizza_type,
        "num_people": num_people,
        "stuffed": stuffed_crust
    })
    return "{\"status\":200, \"message\": \"ok\", \"items\": " + cart["items"] + "}", 200
if __name__ == "__main__":
    app.run()