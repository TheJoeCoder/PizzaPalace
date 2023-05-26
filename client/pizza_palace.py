import json
from tkinter import ttk, messagebox

## Init
root = Tk()

## Global Variables
name = StringVar()
age = StringVar()

## Subroutines
def submit(*args):
    messagebox.showinfo("Not implemented")

## Main program code
root.title("Pizza Palace")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


name_label = ttk.Label(mainframe, text="Pizza Type: ")
name_label.grid(column=1, row=1, sticky=(W, E))
name_entry = ttk.Entry(mainframe, width=10, textvariable=name)
name_entry.grid(column=2, row=1, sticky=(W, E))

age_label = ttk.Label(mainframe, text="Age: ")
age_label.grid(column=1, row=2, sticky=(W, E))
age_entry = ttk.Entry(mainframe, width=10, textvariable=age)
age_entry.grid(column=2, row=2, sticky=(W, E))

submit_button = ttk.Button(mainframe, text="Go!", command=submit)
submit_button.grid(column=2, row=3, sticky=(W, E))

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

name_entry.focus()
root.bind("<Return>", submit)

root.mainloop()
