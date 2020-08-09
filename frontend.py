import tkinter as tk
from database import Database

db = Database()
def nicks_stuff():
    """
    Insert backend stuff here
    """
    student_id = ent_student_id.get()
    password = int(ent_password.get())
    days = int(ent_days.get())
    stud_id = db.validate_login(student_id, password)
    response = db.formatted_interactions(stud_id, days)

    lbl_result["text"] = response

# Set-up the window
window = tk.Tk()
window.title("How Many Interactions Did I Have?")
window.resizable(width=True, height=True)

# Create the Fahrenheit entry frame with an Entry
# widget and label in it
frm_entry_us = tk.Frame(master=window)
ent_student_id = tk.Entry(master=frm_entry_us, width=10)
lbl_student_id = tk.Label(master=frm_entry_us, text="Your Student ID             ")

# Create the Fahrenheit entry frame with an Entry
# widget and label in it
frm_entry_pw = tk.Frame(master=window)
ent_password = tk.Entry(master=frm_entry_pw, width=10, show='*')
lbl_password = tk.Label(master=frm_entry_pw, text="Your PIN #                     ")

# Create the Fahrenheit entry frame with an Entry
# widget and label in it
frm_entry_days = tk.Frame(master=window)
ent_days = tk.Entry(master=frm_entry_days, width=10)
lbl_days = tk.Label(master=frm_entry_days, text="Max asymptomatic days")

# Layout the temperature Entry and Label in frm_entry
# using the .grid() geometry manager
ent_student_id.grid(row=0, column=0, sticky="w")
ent_password.grid(row=0, column=1, sticky="w")
ent_days.grid(row=0, column=2, sticky="w")
lbl_student_id.grid(row=0, column=3, sticky="w")
lbl_password.grid(row=0, column=4, sticky="w")
lbl_days.grid(row=0, column=5, sticky="w")

# Create the conversion Button and result display Label
btn_convert = tk.Button(
    master=window,
    text="Submit",
    command=nicks_stuff
)
lbl_result = tk.Label(master=window, text=" ", justify='left')

# Set-up the layout using the .grid() geometry manager
frm_entry_us.grid(row=0, column=0, padx=10)
frm_entry_pw.grid(row=1, column=0, padx=10)
frm_entry_days.grid(row=2, column=0, padx=10)
btn_convert.grid(row=0, column=1, pady=10)
lbl_result.grid(row=0, column=2, padx=10)

# Run the application
window.mainloop()