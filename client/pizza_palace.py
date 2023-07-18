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

orderpage_items = []

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
    item_dict = {}
    for pizza in pizzas:
        if pizza["id"] == item:
            item_dict = pizza
            break
    if item_dict == {}:
        messagebox.showerror("Error", "Could not find pizza")
        return
    res = requests.post(get_endpoint("/cart/add"), json={"id": cart_id, "key": cart_key, "type": item, "num_people": people, "stuffed_crust": stuffed_crust})
    print(res.text)
    if (res.status_code == 200):
        res_json = res.json()
        if (res_json != None and res_json["status"] == 200):
            messagebox.showinfo("OK!", "Successfully added to cart")
        else:
            connect_fail()
    else:
        connect_fail()

class OrderItem():
    def __init__(self, pizza_dict, row):
        global order_frame
        print(pizza_dict)
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

def refresh_order_items(*args):
    global order_frame
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

## Main program code
# Window setup
root.title("Pizza Palace")
tab_control = ttk.Notebook(root)

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

# Confirm tab
confirm_frame = create_tab("Confirm")

# Pack
tab_control.pack(expand=1, fill="both")

# Connect
connect()

# Main window loop
root.mainloop()