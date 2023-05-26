import json, uuid, logging
from flask import Flask, request, jsonify, Response

logger = logging.Logger(__name__)

app = Flask(__name__)

import config

with open("pizza_types.json","r") as f:
    pizza_types = json.loads(f.read())

open_carts = {}

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
    cart_key = str(uuid.uuid4())
    # TODO append cart to list and send to user
    return "{\"status\":200, \"id\": \"not implemented\", \"key\": \"not implemented\"}", 200

if __name__ == "__main__":
    app.run()