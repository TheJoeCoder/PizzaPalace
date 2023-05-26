import json
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

import config

with open("pizza_types.json","r") as f:
    pizza_types = json.loads(f.read())

open_carts = {}

@app.route("/")
def hello_world():
    return "{\"status\":200, \"message\": \"ok\"}", 200

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    return jsonify(pizza_types), 200

@app.route("/cart/open", methods=["POST"])
def open_cart():
    return "{\"status\":404, \"message\": \"not implemented\"}", 404

if __name__ == "__main__":
    app.run()