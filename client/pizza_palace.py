import json
from tkinter import messagebox, ttk
from tkinter import *

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

submit_button = ttk.Button(mainframe, text="Go!", command=submit)
submit_button.grid(column=2, row=3, sticky=(W, E))

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

submit_button.focus()
root.bind("<Return>", submit)

root.mainloop()
