import json, requests
from tkinter import messagebox, ttk
from tkinter import *

## Init
root = Tk()

## Global Variables
connect_url = StringVar()

## Subroutines
def get_endpoint(endpoint):
    return connect_url.get() + endpoint

def submit(*args):
    messagebox.showinfo("Not implemented", "Not just yet...")

def connect(*args):
    try:
        res = requests.get(get_endpoint("/"))
        if res.status_code == 200:
            # Success
            # TODO check for valid JSON response, possibly change to /status endpoint
            messagebox.showinfo("OK!", "Successfully connected")
            connect_status_label.configure(text="Connected")
            # TODO focus on other tab
        else:
            # Failure
            # TODO failure message
            pass
    except:
        # Failure
        # TODO failure message
        pass

## Main program code
root.title("Pizza Palace")
tab_control = ttk.Notebook(root)

connect_frame = ttk.Frame(tab_control, padding="3 3 12 12")
connect_frame.grid(column=0, row=0, sticky=(N, W, E, S))
connect_frame.columnconfigure(0, weight=1)
connect_frame.rowconfigure(0, weight=1)

connect_url_label = ttk.Label(connect_frame, text="Server URL:")
connect_url_field = ttk.Entry(connect_frame, width=20, textvariable=connect_url)
connect_url_label.grid(column=1, row=1, sticky=(W, E))
connect_url_field.grid(column=2, row=1, sticky=(W, E))
connect_url.set("http://localhost:5000")

connect_status_label = ttk.Label(connect_frame, text="Not connected")
connect_status_label.grid(column=1, row=2, sticky=(W, E))

connect_submit_button = ttk.Button(connect_frame, text="Go!", command=connect)
connect_submit_button.grid(column=1, row=3, sticky=(W, E))

for child in connect_frame.winfo_children():
    child.grid_configure(padx=5, pady=5)

connect_submit_button.focus()
connect_frame.bind("<Return>", submit)

# TODO other tabs

tab_control.add(connect_frame, text="Connect")
tab_control.pack(expand=1, fill="both")

root.mainloop()
