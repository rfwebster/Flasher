import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime
import csv
import os

LOG_FILE = 'C:/Data/logger/log.csv'

_status = 0  # online
try:
    from PyJEM import detector, TEM3
    TEM3.connect()
except ImportError:
    from PyJEM.offline import detector, TEM3
    _status = 1  # offline

LOG_FILE = "C:/Data/logger/log.csv"


class Window(tk.Tk):
    checkbuttons_var = []

    HT = TEM3.HT3()
    gun = TEM3.GUN3()

    csv_header = ["datetime", "user",
        "Sample in?", "LN2 Filled?",
        "SIP 1", "SIP 2", "SIP 200", "SIP 3",
        "HT", "EC",
        "A1", "A2",
        "Flash Type",
        "Notes"]

    def __init__(self):
        super().__init__()
        self.title("Flash Logger!")
        self.geometry("412x460")



        self.previousentry = None

        self.create_widgets()
        self.check_file_exists(LOG_FILE)
        self.update_text_labels()

    def create_widgets(self):
        # code to create the Tkinter widgets and layout them goes here
        PAD_X = 5
        PAD_Y = 5
        self.centralwidget = tk.Frame(self)
        self.centralwidget.pack(fill=tk.BOTH, expand=True)

        self.gridLayoutWidget = tk.Frame(self.centralwidget)
        self.gridLayoutWidget.pack(padx=PAD_X, pady=PAD_Y)

        self.comboBox = ttk.Combobox(self.gridLayoutWidget, values=["High Flash", "Low Flash"], state="readonly")
        self.comboBox.grid(row=3, column=0, pady=PAD_Y)

        self.notebox = tk.Text(self.gridLayoutWidget, height=5, width=40)
        self.set_notebox_text()
        self.notebox.bind("<FocusIn>", self.clear_notebox_text)

        self.notebox.grid(row=4, column=0, pady=PAD_Y)

        self.startButton = ttk.Button(self.gridLayoutWidget, text="Log!", command=self.go)
        self.startButton.grid(row=5, column=0, pady=PAD_Y)

        self.sample_checkbutton_var = tk.BooleanVar()
        self.sample_checkbutton = ttk.Checkbutton(self.gridLayoutWidget, text="Sample In", variable=self.sample_checkbutton_var)
        self.sample_checkbutton.grid(row=1, column=0, pady=PAD_Y)
        self.checkbuttons_var.append(self.sample_checkbutton_var)

        self.useredit = ttk.Entry(self.gridLayoutWidget)
        self.set_user_text()
        self.useredit.bind("<FocusIn>", self.clear_user_text    )
        self.useredit.grid(row=0, column=0, pady=PAD_Y)

        self.ln2_checkbutton_var = tk.BooleanVar()
        self.ln2_checkbutton = ttk.Checkbutton(self.gridLayoutWidget, text="Liquid Nitrogen Filled", variable=self.ln2_checkbutton_var)
        self.ln2_checkbutton.grid(row=2, column=0, pady=PAD_Y)
        self.checkbuttons_var.append(self.ln2_checkbutton_var)


        self.groupBox = ttk.LabelFrame(self.centralwidget, text="Last Flash:")
        self.groupBox.pack(padx=PAD_X, pady=PAD_Y)

        self.formLayoutWidget = tk.Frame(self.groupBox)
        self.formLayoutWidget.pack(padx=PAD_X, pady=PAD_Y)

        self.label = ttk.Label(self.formLayoutWidget, text="Date/Time:")
        self.label.grid(row=0, column=0, padx=PAD_X)

        self.datetime_label = ttk.Label(self.formLayoutWidget, text="yyyy/mm/dd 00:00")
        self.datetime_label.grid(row=0, column=1, padx=PAD_X)

        self.label_2 = ttk.Label(self.formLayoutWidget, text="Type:")
        self.label_2.grid(row=1, column=0, padx=PAD_X)

        self.flash_label = ttk.Label(self.formLayoutWidget, text="High Flash")
        self.flash_label.grid(row=1, column=1, padx=PAD_X)

        self.status_bar = ttk.Label(self, text="", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.set_status("Welcome to the Emission Logger!")

         # Add other Tkinter widgets as needed

    def set_status(self, message):
        self.status_bar.config(text=message)

    def clear_user_text(self, e):
        self.useredit.delete(0,tk.END)
    
    def set_user_text(self):
        self.useredit.delete(0,tk.END)
        self.useredit.insert(tk.END, "User Name")

    def get_user_text(self):
        text_content = self.useredit.get()
        text_content = text_content.replace("\n", "")  # Remove newlines
        return text_content

    def clear_notebox_text(self, e):
        self.notebox.delete("1.0",tk.END)
    
    def set_notebox_text(self):
        self.notebox.delete("1.0", tk.END)
        self.notebox.insert(tk.END, "Notes")

    def get_notebox_text(self):
        text_content = self.notebox.get("1.0", tk.END)
        text_content = text_content.replace("\n", "")  # Remove newlines
        return text_content

    def check_file_exists(self, file_path):
        if not os.path.exists(file_path):
            directory, filename = os.path.split(file_path)
            os.makedirs(directory)
            with open(file_path, "w", newline="", encoding="utf-8") as f:

                writer = csv.writer(f)
                writer.writerow(self.csv_header)

    def read_last_line(self, file_path):
        # Your implementation to read the last line of the CSV file and return it as a list
        if not os.path.exists(file_path):
            directory, filename = os.path.split(file_path)
            os.makedirs(directory)
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.csv_header)

            #logging.error("Please close the .csv file and restart the program")
            self.set_status("Please close the csv file and restart the program")
            return None
        
        try:
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                lines = f.readlines()
                last_line = lines[-1].strip().split(',') if len(lines) > 0 else None
                return last_line

        except PermissionError:
            #logging.error("Please close the .csv file and restart the program")
            self.set_status("Please close the csv file and restart the program")
            return None
        
    def add_line_to_csv(self, file_path, variables):
        # Your implementation to add a new line to the CSV file with the given data
        try:
            with open(file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(variables)
        except PermissionError: 
            #logging.error("Please close the .csv file and restart the program")
            self.set_status("Please close the csv file and restart the program")

    def update_text_labels(self):
        # Your implementation to update the date and time and flash type labels
        # based on the last entry in the CSV file
        self.previousentry = self.read_last_line(LOG_FILE)
        if self.previousentry is not None:
            print(self.previousentry)
            #print(self.previousentry[0], self.previousentry[12])
            self.datetime_label.config(text=self.previousentry[0])
            #self.flash_label.config(text=self.previousentry[12])

    def go(self):
    #     # Your implementation to retrieve the current values of the user input fields
    #     # and add a new line to the CSV file using add_line_to_csv, then reset the input fields
        self.datetime = datetime.now()
        self.datetime = self.datetime.strftime("%Y-%m-%d %H:%M")
        self.ht = self.HT.GetHtValue()
        self.EC = self.gun.GetEmissionCurrentValue()
        self.A1 = self.gun.GetAnode1CurrentValue()
        self.A2 = self.gun.GetAnode2CurrentValue()
        self.user = self.get_user_text()
        self.flashtype = self.comboBox.get()
        self.notes = self.get_notebox_text()
        self.samplein = self.sample_checkbutton_var.get()
        self.ln2 = self.ln2_checkbutton_var.get()
        self.add_line_to_csv(LOG_FILE, [
            self.datetime, self.user,
            self.samplein, self.ln2,
            "SIP 1", "SIP 2", "SIP 200", "SIP 3",
            self.ht, self.EC,
            self.A1, self.A2,
            self.flashtype,
            self.notes]
        )
        self.reset()

    def reset(self):
        # implementation to clear the user input fields and uncheck the checkboxes
        self.uncheck_all_checkbuttons()
        self.update_text_labels()
        self.set_notebox_text()
        self.set_user_text()
        return 0
    
    def uncheck_all_checkbuttons(self):
        # implementation to uncheck all checkboxes
        for checkbutton_var in self.checkbuttons_var:
            checkbutton_var.set(False)


if __name__ == "__main__":
    app = Window()
    app.mainloop()
