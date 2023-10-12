import json, uuid, logging, requests, time
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

logger = logging.Logger(__name__)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
socketio = SocketIO(app)

import config

# Connect to MongoDB
client = MongoClient(config.mongo_uri)

db = client[config.mongo_db]

start_time = time.time()

with open("pizza_types.json","r") as f:
    pizza_types = json.loads(f.read())

open_carts = {}

open_carts["test"] = {
    "key": "test",
    "items": []
}

# Generate admin token
admin_token = str(uuid.uuid4())
print("Admin token: " + admin_token)

# Full stack trace function
#  from https://stackoverflow.com/questions/6086976/how-to-get-a-complete-exception-stack-trace-in-python/16589622#16589622 
def full_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

def get_cart(uid, key):
    if (uid == None or key == None or uid not in open_carts or open_carts[uid]["key"] != key):
        return None
    return open_carts[uid]

def gen_invalid_creds_msg():
    return "{\"status\":403, \"message\": \"invalid cart credentials\"}", 403

def gen_invalid_message(noun: str):
    return "{\"status\":400, \"message\": \"invalid " + noun + "\"}", 400

def gen_missing_message(noun: str):
    return "{\"status\":400, \"message\": \"missing " + noun + "\"}", 400

def get_property(request, param):
    if (request.headers.get("Content-Type") == "application/json" and request.json.get(param) != None):
        return request.json.get(param)
    elif (request.args.get(param) != None):
        return request.args.get(param)
    else:
        return None

def fancy_order_display(cart_items) -> str:
    i_items = ""
    if len(cart_items) == 0:
        i_items = "No items\n"
    for item in cart_items:
        pza = None
        for p in pizza_types:
            if p["id"] == item["type"]:
                pza = p
                break
        if pza == None:
            i_items += "Unknown pizza type\n"
        else:
            i_items += pza["name"] + " (" + str(item["num_people"]) + " people) " + ("stuffed" if item["stuffed"] else "") + "\n"
    i_items = i_items[:-1] # Remove trailing \n
    return i_items

@app.route("/")
def hello_world():
    # Return OK message
    return "{\"status\":200, \"message\": \"ok\"}", 200

@app.route("/admin")
def admin_page_index():
    return render_template("admin.html")

@app.route("/status", methods=["GET"])
def get_status():
    # Return status
    return "{\"status\":200, \"message\": \"ok\", \"uptime\": " + str(time.time() - start_time) + "}", 200

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
        if (cart_id in open_carts):
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
    cart_id = get_property(request, "id")
    cart_key = get_property(request, "key")
    # Get cart and verify not none
    cart = get_cart(cart_id, cart_key)
    if (cart == None):
        return gen_invalid_creds_msg()
    return "{\"status\":200, \"items\": " + json.dumps(cart["items"]) + "}", 200

@app.route("/cart/add", methods=["POST"])
def add_cart_item():
    # Get cart id and key from request
    cart_id = get_property(request, "id")
    cart_key = get_property(request, "key")
    # Get cart and verify not none
    cart = get_cart(cart_id, cart_key)
    if (cart == None):
        return gen_invalid_creds_msg()
    # Get pizza type from request
    pizza_type = get_property(request, "type")
    if (pizza_type == None):
        return gen_missing_message("pizza type")
    # Get pizza type (ID) from pizza types
    pizza_type_obj = None
    for type in pizza_types:
        if (type["id"] == pizza_type):
            pizza_type_obj = type
            break
    if (pizza_type_obj == None):
        return gen_invalid_message("pizza type")
    # Get number of people from request
    num_people = get_property(request, "num_people")
    if (num_people == None):
        return gen_missing_message("number of people")
    # Test for invalid number of people and convert to integer
    try:
        num_people = int(num_people)
    except:
        return gen_invalid_message("number of people")
    # Get stuffed crust from request
    stuffed_crust = get_property(request, "stuffed_crust")
    if (stuffed_crust == None):
        return gen_missing_message("stuffed crust")
    # Test for invalid stuffed crust and convert to boolean
    stuffed_crust = str(stuffed_crust) # Convert to string to avoid errors
    if (stuffed_crust.lower() == "true"):
        stuffed_crust = True
    elif (stuffed_crust.lower() == "false"):
        stuffed_crust = False
    else:
        return gen_invalid_message("stuffed crust")
    cart["items"].append({
        "type": pizza_type,
        "num_people": num_people,
        "stuffed": stuffed_crust
    })
    return "{\"status\":200, \"message\": \"ok\", \"items\": " + json.dumps(cart["items"]) + "}", 200

@app.route("/cart/total", methods=["GET"])
def get_cart_total():
    # Get cart id and key from request
    cart_id = get_property(request, "id")
    cart_key = get_property(request, "key")
    # Get cart and verify not none
    cart = get_cart(cart_id, cart_key)
    if (cart == None):
        return gen_invalid_creds_msg()
    subtotal = 0.0
    breakdown = []
    for item in cart["items"]:
        for pizza in pizza_types: # TODO optimise; REALLY inefficient
            if (pizza["id"] == item["type"]):
                # Found correct pizza
                i_main_subtotal = item["num_people"] * pizza["cost_pp"]
                i_breakdown = {
                    "item": pizza["id"],
                    "cost_per": pizza["cost_pp"],
                    "num_people": item["num_people"],
                    "base_total": i_main_subtotal,
                    "addons": []
                }
                i_breakdown["total"] = i_main_subtotal
                subtotal += i_main_subtotal
                if (item["stuffed"]):
                    i_stuffed_total = item["num_people"] * pizza["stuffed_pp"]
                    i_breakdown["addons"].append({
                        "name": "stuffed",
                        "cost_per": pizza["stuffed_pp"],
                        "addon_total": i_stuffed_total
                    })
                    i_breakdown["total"] = i_main_subtotal + i_stuffed_total
                    subtotal += i_stuffed_total
                breakdown.append(i_breakdown)
                break
    grand_total = subtotal + config.delivery_flatrate
    return "{\"status\":200,\"message\":\"ok\",\"subtotal\":" + str(subtotal) + ",\"delivery_rate\":" + str(config.delivery_flatrate) + ",\"total\":" + str(grand_total) + ",\"breakdown\":" + json.dumps(breakdown) + "}", 200

@app.route("/cart/confirmorder", methods=["POST"])
def confirm_order_cart():
    # Get cart id and key from request
    cart_id = get_property(request, "id")
    cart_key = get_property(request, "key")
    # Get cart and verify not none
    cart = get_cart(cart_id, cart_key)
    if (cart == None):
        return gen_invalid_creds_msg()
    address = get_property(request, "address")
    if (address == None):
        return gen_missing_message("address")
    # Test for invalid address and convert to dict
    #print(address)
    #try:
    #    address = json.loads(address)
    #except:
    #    return gen_invalid_message("address")
    # Build order
    order = {
        "address": address,
        "items": cart["items"]
    }
    # Add order to database
    order_id = db.orders.insert_one(order).inserted_id
    # Post webhook
    webhook_data = {
        "username": "PizzaBot"
    }
    if config.webhook_discord:
        i_items = fancy_order_display(cart["items"])
        # Post webhook
        embed = config.webhook_dc_embed_json.copy()
        for i in range(0, len(embed["fields"])):
            print(embed["fields"][i])
            for field_k, field_v in embed["fields"][i].items():
                value = str(field_v)
                value = value.replace("%ORDER_ID%", str(order_id))
                value = value.replace("%ADDRESS%", str(address))
                value = value.replace("%ITEMS%", i_items)
                embed["fields"][i][field_k] = value
        webhook_data["embeds"] = [embed]
        webhook_data["content"] = config.webhook_dc_embed_msg
    else:
        webhook_data["content"] = config.webhook_content_prepend + str(order_id)
    print(json.dumps(webhook_data))
    try:
        webhook_response = requests.post(config.webhook_url, json=webhook_data)
        if (webhook_response.status_code != 200):
            logger.error("Webhook failed with status code " + str(webhook_response.status_code))
    except:
        except_text = full_stack()
        logger.error("Webhook failed with exception")
        logger.debug(except_text)
    socketio.emit("order create", {"id": str(order_id), "address": address, "items": fancy_order_display(cart["items"]).replace("\n", "<br>")})
    # Remove cart from existing carts
    del open_carts[cart_id]
    # Return order ID
    return "{\"status\":200,\"message\":\"ok\", \"code\":\"" + str(order_id) + "\"}", 200

# Main program code
if (__name__ == "__main__"):
    socketio.run(app, debug=True, host="0.0.0.0")