import json, requests, logging
from tkinter import messagebox, ttk
from tkinter import *

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
    for child in connect_frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

# General connect fail function
# Used when the server is unreachable or returns a non-200 response
#  both in the initial connection attempt and in other screens
#  where a server request is made
def connect_fail():
    logger.error("Connection Failed")
    connect_status_label.configure(text="Connection failed")
    tab_control.select(connect_frame)
    messagebox.showerror("Connection failed", "Could not connect to server")

# Request session fail function
def request_session_fail():
    logger.error("Request session failed")
    connect_status_label.configure(text="Request session failed")
    tab_control.select(connect_frame)
    messagebox.showerror("Request session failed", "Could not request session")

# Connection success function
# Used when the server is reachable and all is ok
#  in the initial connection attempt
def connect_success():
    logger.info("Successfully connected to " + connect_url.get())
    connect_status_label.configure(text="Connected")
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
    pass

class OrderItem():
    def __init__(self, pizza_dict, col):
        self.id = pizza_dict.id
        self.col = col
        self.label1 = ttk.Label(order_frame, text=pizza_dict.name)
        self.label1.grid(column=col, row=1, sticky=(W, E))
        self.label2 = ttk.Label(order_frame, text="£%.2f" % pizza_dict.costpp)
        self.label2.grid(column=col, row=2, sticky=(W, E))
        # TODO number of people
        self.quantity = IntVar(value=1)
        # self.quant_entry = ttk.Spinbox(order_frame, from=1, to=99)
        # TODO stuffed crust
        self.stuffed_crust = BooleanVar()
        self.order_butt = ttk.Button(order_frame, text="Order", command=self.order)
        self.order_butt.grid(column=col, row=4, sticky=(W, E))
    def order(self):
        order_item(self.id, self.quantity.get(), self.stuffed_crust.get())

def refresh_order_items(*args):
    global order_frame
    if(refresh_items()):
        # Remove all items
        for op_item in orderpage_items:
            for op_childitem in op_item:
                op_childitem.destroy()
                del op_childitem
            del op_item
        col = 1
        for pizza in pizzas:
            piz_label1 = ttk.Label(order_frame, text=pizza.name)
            piz_label1.grid(column=col, row=1, sticky=(W, E))
            piz_label2 = ttk.Label(order_frame, text="£%.2f" % pizza.costpp)
            piz_label2.grid(column=col, row=2, sticky=(W, E))
            piz_orderbutton = ttk.Button(order_frame, text="Order", command=lambda: order_item())


## Main program code
# Window setup
root.title("Pizza Palace")
tab_control = ttk.Notebook(root)

# Connect tab
connect_frame = create_tab("Connect")

connect_url_label = ttk.Label(connect_frame, text="Server URL:")
connect_url_field = ttk.Entry(connect_frame, width=20, textvariable=connect_url)
connect_url_label.grid(column=1, row=1, sticky=(W, E))
connect_url_field.grid(column=2, row=1, sticky=(W, E))
connect_url.set("http://localhost:5000")

connect_status_label = ttk.Label(connect_frame, text="Not connected")
connect_status_label.grid(column=1, row=2, sticky=(W, E))

connect_submit_button = ttk.Button(connect_frame, text="Go!", command=connect)
connect_submit_button.grid(column=1, row=3, sticky=(W, E))

configure_grid(connect_frame)

connect_submit_button.focus()
connect_frame.bind("<Return>", connect)

# Order tab
order_frame = create_tab("Order")
refresh_order_items()

# Cart tab
cart_frame = create_tab("Cart")

# Confirm tab
confirm_frame = create_tab("Confirm")


# Pack
tab_control.pack(expand=1, fill="both")

# Main window loop
root.mainloop()
