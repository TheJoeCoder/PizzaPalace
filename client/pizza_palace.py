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

cart_id = ""
cart_key = ""

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

# Connection success fail function
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
                    connect_success()
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
    
    pass

# Refresh order screen items
def refresh_items(*args):
    # TODO get /pizzas from server
    pass

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
# TODO order list

# Cart tab
cart_frame = create_tab("Cart")

# Confirm tab
confirm_frame = create_tab("Confirm")


# Pack
tab_control.pack(expand=1, fill="both")

# Main window loop
root.mainloop()
