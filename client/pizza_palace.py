import json, requests, logging
from tkinter import messagebox, ttk
from tkinter import *

## Server URL
server_url = "http://localhost:5000"

## Init
root = Tk()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

## Global Variables
connect_url = StringVar()

pizzas = []

cart_id = ""
cart_key = ""

req_cart_items = []

orderpage_items = []
cartpage_items = []

## Subroutines
def get_endpoint(endpoint):
    return connect_url.get() + endpoint

def validate_int(input):
    try:
        unused = int(input)
        return True
    except:
        return False
validate_int_command = (root.register(validate_int), "%P")

# Create frame
def create_tab(title, padding="3 3 12 12", sticky=(N, W, E, S)):
    frame = ttk.Frame(tab_control, padding=padding)
    frame.grid(column=0, row=0, sticky=sticky)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    tab_control.add(frame, text=title)
    return frame

# Configure grid for frame
def configure_grid(frame):
    for child in frame.winfo_children():
        child.grid_configure(padx=5, pady=5)
    frame.pack(expand=1, fill="both") ## TEST

# General connect fail function
# Used when the server is unreachable or returns a non-200 response
#  both in the initial connection attempt and in other screens
#  where a server request is made
def connect_fail():
    logger.error("Connection Failed")
    #connect_status_label.configure(text="Connection failed")
    #tab_control.select(connect_frame)
    messagebox.showerror("Connection failed", "Could not connect to server")

# Request session fail function
def request_session_fail():
    logger.error("Request session failed")
    #connect_status_label.configure(text="Request session failed")
    #tab_control.select(connect_frame)
    messagebox.showerror("Request session failed", "Could not request session")

# Connection success function
# Used when the server is reachable and all is ok
#  in the initial connection attempt
def connect_success():
    logger.info("Successfully connected to " + connect_url.get())
    #connect_status_label.configure(text="Connected")
    tab_control.select(order_frame)
    messagebox.showinfo("OK!", "Successfully connected")

# Connect function for the connect tab
def connect(*args):
    logger.info("Attempting to connect to " + connect_url.get())
    try:
        res = requests.get(get_endpoint("/status"))
        if (res.status_code == 200):
            # Success
            logger.debug("Got 200 response from server")
            try:
                res_json = json.loads(res.text)
                if (res_json["status"] == 200 and res_json["message"] == "ok"):
                    # Request session
                    logger.debug("Got OK response from server")
                    if (new_session()):
                        refresh_order_items()
                        connect_success()
                        return
                    request_session_fail()
                    return
                else:
                    logger.debug("Response from server did not contain OK")
                    connect_fail()
                    return
            except:
                logger.debug("Could not parse JSON response from server")
                logger.debug(res.text)
                connect_fail()
                return
        else:
            logger.debug("Got non-200 response from server")
            connect_fail()
            return
    except:
        connect_fail()
        return

# Create new session
def new_session(*arg):
    global cart_id, cart_key
    res = requests.post(get_endpoint("/cart/open"))
    if (res.status_code == 200):
        res_json = res.json()
        if (res_json != None and res_json["status"] == 200):
            cart_id, cart_key = res_json["id"], res_json["key"]
            logger.debug("Cart ID: " + cart_id)
            logger.debug("Cart Key: " + cart_key)
            return True
        else:
            return False
    else:
        return False

# Refresh order screen items
def refresh_items():
    global pizzas
    res = requests.get(get_endpoint("/pizzas"))
    if (res.status_code == 200 and res.json() != None):
        pizzas = res.json()
        return True
    else:
        connect_fail()
        return False

def order_item(item, people, stuffed_crust):
    global pizzas, cart_id, cart_key
    item_dict = {}
    for pizza in pizzas:
        if pizza["id"] == item:
            item_dict = pizza
            break
    if item_dict == {}:
        messagebox.showerror("Error", "Could not find pizza")
        return
    reqjson = {"id": cart_id, "key": cart_key, "type": item, "num_people": people, "stuffed_crust": stuffed_crust}
    res = requests.post(get_endpoint("/cart/add"), json=reqjson)
    logger.debug(res.text)
    if (res.status_code == 200):
        res_json = res.json()
        if (res_json != None and res_json["status"] == 200):
            # Success
            # Refresh items
            refresh_order_items()
            # Message box
            messagebox.showinfo("OK!", "Successfully added to cart")
        else:
            connect_fail()
    else:
        connect_fail()

class OrderItem():
    def __init__(self, pizza_dict, row):
        global order_frame
        self.id = pizza_dict["id"]
        self.row = row
        self.label1 = ttk.Label(order_frame, text=pizza_dict["name"])
        self.label1.grid(column=1, row=row, sticky=(W, E))
        self.label2 = ttk.Label(order_frame, text="£%.2f" % pizza_dict["cost_pp"])
        self.label2.grid(column=2, row=row, sticky=(W, E))
        self.quantity = StringVar(value=1)
        self.quant_entry = ttk.Spinbox(order_frame, from_=1, to=99, textvariable=self.quantity, validate="focusout", validatecommand=validate_int_command)
        self.quant_entry.grid(column=3, row=row, sticky=(W, E))
        self.stuffed_crust = BooleanVar(value=False)
        self.stuffed_entry = ttk.Checkbutton(order_frame, variable=self.stuffed_crust)
        self.stuffed_entry.grid(column=4, row=row, sticky=(W, E))
        self.order_butt = ttk.Button(order_frame, text="Order", command=self.order)
        self.order_butt.grid(column=5, row=row, sticky=(W, E))
    def destroy(self):
        self.label1.destroy()
        self.label2.destroy()
        self.quant_entry.destroy()
        self.stuffed_entry.destroy()
        self.order_butt.destroy()
    def order(self):
        if (validate_int(self.quantity.get())):
            order_item(self.id, int(self.quantity.get()), self.stuffed_crust.get())

def refresh_order_items():
    global order_frame, pizzas, orderpage_items
    if(refresh_items()):
        # Remove all items
        for op_item in orderpage_items:
            op_item.destroy()
            del op_item
        row = 2
        for pizza in pizzas:
            orderpage_items.append(OrderItem(pizza, row))
            row += 1
    configure_grid(order_frame)

# Refresh cart screen items
class CartItem():
    def __init__(self, item_dict, row):
        global cart_frame, pizzas
        self.id = item_dict["type"]
        self.pizza = None
        for p in pizzas:
            if p["id"] == self.id:
                self.pizza = p
                break
        if self.pizza == None:
            logger.error("Could not find pizza with ID " + self.id)
            return
        self.row = row
        self.label1 = ttk.Label(cart_frame, text=self.pizza["name"])
        self.label1.grid(column=1, row=row, sticky=(W, E))
        self.label2 = ttk.Label(cart_frame, text=str(item_dict["num_people"]))
        self.label2.grid(column=2, row=row, sticky=(W, E))
        self.stuffed_crust = BooleanVar(value=item_dict["stuffed"])
        self.stuffed_display = ttk.Checkbutton(cart_frame, variable=self.stuffed_crust, state="disabled")
        self.stuffed_display.grid(column=3, row=row, sticky=(W, E))
        self.label3 = ttk.Label(cart_frame, text="£%.2f" % (float(self.pizza["cost_pp"]) * int(item_dict["num_people"])))
        self.label3.grid(column=4, row=row, sticky=(W, E))
    def destroy(self):
        self.label1.destroy()
        self.label2.destroy()
        self.stuffed_display.destroy()

def refresh_citems():
    global req_cart_items
    reqjson = {"id": cart_id, "key": cart_key}
    res = requests.get(get_endpoint("/cart/items"), params=reqjson)
    if (res.status_code == 200 and res.json() != None):
        items = res.json()["items"]
        req_cart_items = items
        return True
    else:
        connect_fail()
        return False

def refresh_cart_items():
    global cart_frame, cartpage_items
    if(refresh_citems()):
        # Remove all items
        for c_item in cartpage_items:
            c_item.destroy()
            del c_item
        # Add all items back
        row = 2
        for item in req_cart_items:
            orderpage_items.append(CartItem(item, row))
            row += 1
        configure_grid(cart_frame)

def confirm_order(address_vars: dict):
    global cart_id, cart_key
    # Check all address fields are filled
    for var in address_vars:
        if (var.get() == ""):
            messagebox.showerror("Error", "Please fill in all address fields")
            return
    # Check cart is not empty
    if (len(req_cart_items) == 0):
        messagebox.showerror("Error", "Cart is empty")
        return
    # Join address fields
    address = ""
    for var in address_vars:
        address += var.get() + ", "
    address = address[:-2]
    # Confirm order
    reqjson = {"id": cart_id, "key": cart_key, "address": address}
    res = requests.post(get_endpoint("/cart/confirmorder"), json=reqjson)
    if (res.status_code == 200):
        req_cart_items = []
        refresh_cart_items()
        new_session()
        tab_control.select(order_frame)
        messagebox.showinfo("OK!", "Order confirmed")

def tab_changed_handler(event):
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")
    if (tab_text == "Order"):
        refresh_order_items()
    elif (tab_text == "Cart"):
        refresh_cart_items()

## Main program code
# Window setup
root.title("Pizza Palace")
tab_control = ttk.Notebook(root)
tab_control.bind("<<NotebookTabChanged>>", tab_changed_handler)

# Connect tab
#connect_frame = create_tab("Connect")

#connect_url_label = ttk.Label(connect_frame, text="Server URL:")
#connect_url_field = ttk.Entry(connect_frame, width=20, textvariable=connect_url)
#connect_url_label.grid(column=1, row=1, sticky=(W, E))
#connect_url_field.grid(column=2, row=1, sticky=(W, E))
#connect_url.set("http://localhost:5000")

connect_url.set(server_url)

#connect_status_label = ttk.Label(connect_frame, text="Not connected")
#connect_status_label.grid(column=1, row=2, sticky=(W, E))

#connect_submit_button = ttk.Button(connect_frame, text="Go!", command=connect)
#connect_submit_button.grid(column=1, row=3, sticky=(W, E))

#configure_grid(connect_frame)

#connect_submit_button.focus()
#connect_frame.bind("<Return>", connect)

# Order tab
order_frame = create_tab("Order")
order_label_1 = ttk.Label(order_frame, text="Name")
order_label_1.grid(column=1, row=1, sticky=(W, E))
order_label_2 = ttk.Label(order_frame, text="Cost")
order_label_2.grid(column=2, row=1, sticky=(W, E))
order_label_3 = ttk.Label(order_frame, text="Number of People")
order_label_3.grid(column=3, row=1, sticky=(W, E))
order_label_4 = ttk.Label(order_frame, text="Stuffed Crust?")
order_label_4.grid(column=4, row=1, sticky=(W, E))
order_label_5 = ttk.Label(order_frame, text="Order")
order_label_5.grid(column=5, row=1, sticky=(W, E))

configure_grid(order_frame)

# Cart tab

cart_frame = create_tab("Cart")
cart_label_1 = ttk.Label(cart_frame, text="Name")
cart_label_1.grid(column=1, row=1, sticky=(W, E))
cart_label_2 = ttk.Label(cart_frame, text="Number of People")
cart_label_2.grid(column=2, row=1, sticky=(W, E))
cart_label_3 = ttk.Label(cart_frame, text="Stuffed Crust?")
cart_label_3.grid(column=3, row=1, sticky=(W, E))
cart_label_4 = ttk.Label(cart_frame, text="Total Cost")
cart_label_4.grid(column=4, row=1, sticky=(W, E))

cart_order_button = ttk.Button(cart_frame, text="Order", command=lambda: tab_control.select(confirm_frame))
cart_order_button.grid(column=1, row=2, sticky=(W, E))

configure_grid(cart_frame)

# Confirm tab
confirm_frame = create_tab("Confirm")

confirm_addressline1 = StringVar()
confirm_addressline2 = StringVar()
confirm_city = StringVar()
confirm_postcode = StringVar()

confirm_label_1 = ttk.Label(confirm_frame, text="Address Line 1")
confirm_label_1.grid(column=1, row=1, sticky=(W, E))
confirm_entry_1 = ttk.Entry(confirm_frame, width=20, textvariable=confirm_addressline1)
confirm_entry_1.grid(column=2, row=1, sticky=(W, E))

confirm_label_2 = ttk.Label(confirm_frame, text="Address Line 2")
confirm_label_2.grid(column=1, row=2, sticky=(W, E))
confirm_entry_2 = ttk.Entry(confirm_frame, width=20, textvariable=confirm_addressline2)
confirm_entry_2.grid(column=2, row=2, sticky=(W, E))

confirm_label_3 = ttk.Label(confirm_frame, text="City")
confirm_label_3.grid(column=1, row=3, sticky=(W, E))
confirm_entry_3 = ttk.Entry(confirm_frame, width=20, textvariable=confirm_city)
confirm_entry_3.grid(column=2, row=3, sticky=(W, E))

confirm_label_4 = ttk.Label(confirm_frame, text="Postcode")
confirm_label_4.grid(column=1, row=4, sticky=(W, E))
confirm_entry_4 = ttk.Entry(confirm_frame, width=20, textvariable=confirm_postcode)
confirm_entry_4.grid(column=2, row=4, sticky=(W, E))

confirm_button_1 = ttk.Button(confirm_frame, text="Confirm", command=lambda: confirm_order([confirm_addressline1, confirm_addressline2, confirm_city, confirm_postcode]))

# Pack
tab_control.pack(expand=1, fill="both")

# Connect
connect()

# Main window loop
root.mainloop()