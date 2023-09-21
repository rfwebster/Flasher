import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from datetime import datetime
import csv
import os

import threading
import time

LOG_FILE = 'C:/Data/flasher/log.csv'

_status = 0  # online
try:
    from PyJEM import detector, TEM3
    TEM3.connect()
except ImportError:
    from PyJEM.offline import detector, TEM3
    _status = 1  # offline

LOG_FILE = "C:/Data/flasher/log.csv"


class FlashListener(threading.Thread):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.daemon = True  # Set the thread as a daemon, so it stops when the main program exits

    def run(self):
        while True:
            # Determine the flash type based on the current emission and last flash time
            flash_type = self.window.get_flash_type()

            # Update the status label
            self.window.set_status("Emission Current: {}uA".format(self.window.get_emission()))

            self.window.update_instruction_label(flash_type)

            # Sleep for one minute
            time.sleep(60)


class Window(tk.Tk):
    checkbuttons_var = []

    HT = TEM3.HT3()
    gun = TEM3.GUN3()
    stage = TEM3.Stage3()

    csv_header = ["datetime", "user",
        "Sample in?", "LN2 Filled?",
        "SIP 1", "SIP 2", "SIP 200", "SIP 3",
        "HT", "EC",
        "A1", "A2",
        "Flash Type",
        "Notes"]

    def __init__(self):
        super().__init__()

        self.previousentry = None

        self.setup_ui()
        self.check_file_exists(LOG_FILE)
        
        self.update_text_labels()
        
        # Create and start the FlashListener
        self.flash_listener = FlashListener(self)
        self.flash_listener.start()

    def setup_ui(self):
        
        s = ttk.Style()
        s.theme_use('vista')

        PAD_X = 10
        PAD_Y = 5

        self.title("Flasher!")
        self.geometry("350x400")
        self.resizable(0, 0)

        # Create new font objects with the desired font sizes and fonts
        label_font = font.Font(family="Arial", size=12)
        flash_font = ('Arial', 14)
        log_button_font = ('MV Boli', 32)
        s.configure('TLabel', foreground='black', font=label_font)

        s.configure('log.TButton', background='lightblue', foreground='black', font=log_button_font)

        s.configure('low_flash.TLabel', background='orange', foreground='black', font=flash_font)
        s.configure('high_flash.TLabel', background='yellow', foreground='black', font=flash_font)
        s.configure('no_flash.TLabel', background='green', foreground='black', font=flash_font)
        s.configure('unknown_flash.TLabel', background='red', foreground='black', font=flash_font)


        self.mainframe = tk.Frame(self)
        self.mainframe.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)

        self.frame1 = tk.Frame(self.mainframe)
        self.frame1.pack(fill=tk.X)
        
        self.user_label = ttk.Label(self.frame1, text="User Name:", width=10)
        self.user_label.pack(side=tk.LEFT, padx=PAD_X, pady=PAD_Y, )

        self.user_edit = ttk.Entry(self.frame1, font=label_font)
        self.set_user_text("")
        self.user_edit.bind("<FocusIn>", self.clear_user_text)
        self.user_edit.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y, expand=True)

        self.frame2 = tk.Frame(self.mainframe)
        self.frame2.pack(fill=tk.X)        
        self.flash_label = ttk.Label(self.frame2, text="Flash Type:", width=10)
        self.flash_label.pack(side=tk.LEFT, padx=PAD_X, pady=PAD_Y)
        self.comboBox = ttk.Combobox(self.frame2, values=["High Flash", "Low Flash", "No Flash"], state="readonly", font=label_font)
        self.comboBox.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y, expand=True)
       
        self.frame3 = tk.Frame(self.mainframe)
        self.frame3.pack(fill=tk.X)  
        self.flash_label = ttk.Label(self.frame3, text="Liquid N2:", width=10)
        self.flash_label.pack(side=tk.LEFT, padx=PAD_X, pady=PAD_Y, )

        self.ln2_checkbutton_var = tk.BooleanVar()
        self.ln2_checkbutton = tk.Checkbutton(self.frame3, text="Filled", variable=self.ln2_checkbutton_var,
                                              font=label_font)
        self.ln2_checkbutton.pack(padx=PAD_X, pady=PAD_Y)
        self.checkbuttons_var.append(self.ln2_checkbutton_var)


        self.notebox = tk.Text(self.mainframe, height=5, width=40, font=label_font)
        self.set_notebox_text()
        self.notebox.bind("<FocusIn>", self.clear_notebox_text)

        self.notebox.pack(padx=PAD_X, pady=PAD_Y)

        self.instruction_label = ttk.Label(self.mainframe, text="Unknown State :`(", style='unknown.TLabel')
        self.instruction_label.pack(fill='both', padx=PAD_X, pady=PAD_Y, ipadx=PAD_X, ipady=PAD_Y)



        self.startButton = ttk.Button(self.mainframe, text="Log!", command=self.go, style='log.TButton')
        self.startButton.pack(fill='both', padx=PAD_X, pady=2*PAD_Y)


        #progress bar
        self.status_bar = ttk.Label(self, text="", relief=tk.FLAT, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        
    def set_status(self, message):
        self.status_bar.config(text=message)

    def clear_user_text(self, e):
        self.user_edit.delete(0,tk.END)
    
    def set_user_text(self, text):
        self.user_edit.delete(0,tk.END)
        self.user_edit.insert(tk.END, text)

    def get_user_text(self):
        text_content = self.user_edit.get()
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

    def get_last_flash_time(self):
        last_entry = self.read_last_line(LOG_FILE)
        if last_entry:
            last_entry_time_str = last_entry[0]
            return datetime.strptime(last_entry_time_str, "%Y-%m-%d %H:%M")
        else:
            return None
    
    def read_last_line(self, file_path):
        # implementation to read the last line of the CSV file and return it as a list
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
                lines = f.readlines()[1:]
                last_line = lines[-1].strip().split(',') if len(lines) > 0 else None
                return last_line

        except PermissionError:
            #logging.error("Please close the .csv file and restart the program")
            self.set_status("Please close the csv file and restart the program")
            return None
        
    def add_line_to_csv(self, file_path, variables):
        # implementation to add a new line to the CSV file with the given data
        try:
            with open(file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(variables)
        except PermissionError: 
            #logging.error("Please close the .csv file and restart the program")
            self.set_status("Please close the csv file and restart the program")


    def update_instruction_label(self, _status):
        if _status == 0:
            self.instruction_label.config(text="No Action Required", style='no_flash.TLabel')
        elif _status == 1:
            self.instruction_label.config(text="Do a High Flash", style='high_flash.TLabel')
        elif _status == 2:
            self.instruction_label.config(text="Do a Low Flash", style='low_flash.TLabel')
        elif _status == 3:
            self.instruction_label.config(text="Turn off emission and do a Low Flash", style='low_flash.TLabel')
        else:
            self.instruction_label.config(text="Unknown status :\'(", style='unknown_flash.TLabel')
            
    def update_text_labels(self):
        # Method to update the date and time and flash type labels
        # based on the last entry in the CSV file
        self.previousentry = self.read_last_line(LOG_FILE)
        if self.previousentry is not None:
            flash_type = self.get_flash_type()
            self.update_instruction_label(flash_type)


    def get_emission(self):
        return self.gun.GetEmissionCurrentValue()

    def go(self):
    #     # Method to retrieve the current values of the user input fields
    #     # and add a new line to the CSV file using add_line_to_csv, then reset the input fields
        self.datetime = datetime.now()
        self.datetime = self.datetime.strftime("%Y-%m-%d %H:%M")
        self.ht = self.HT.GetHtValue()
        self.EC = self.get_emission()
        self.A1 = self.gun.GetAnode1CurrentValue()
        self.A2 = self.gun.GetAnode2CurrentValue()
        self.user = self.get_user_text()
        self.flashtype = self.comboBox.get()
        self.notes = self.get_notebox_text()
        self.samplein = ("In" if self.stage.GetHolderStts() else "Out")
        self.ln2 = ("Yes" if self.ln2_checkbutton_var.get() else "No")
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


    def get_flash_type(self):
        last_entry = self.read_last_line(LOG_FILE)
        last_flash_time  = self.get_last_flash_time()
        current_time = datetime.now()
        current_emission = self.get_emission()
    
        if last_flash_time.date() == current_time.date(): # has there been a flahs today
            # Check if the emission value is above 12
            if float(last_entry[10]) > 12.0:  # Assuming emission value is in column index 10
                return 0 # do nothing
            # Check if the emission value is below 12
            elif float(last_entry[10]) == 0:
                return 2 # do a low flash
            elif float(last_entry[10]) <= 12.0:  # Assuming emission value is in column index 10
                return 3 # turn off and do low flash
            else:
                return 4  # catch something else
        elif float(last_entry[10]) == 0:
            return 1  # If the times are not from the same day and emission is off, do a high flash
        else:
            return 4 # catch something else


    def reset(self):
        # implementation to clear the user input fields and uncheck the checkboxes
        self.uncheck_all_checkbuttons()
        self.update_text_labels()
        self.set_notebox_text()
        self.set_user_text(" ")
        return 0
    
    def uncheck_all_checkbuttons(self):
        # implementation to uncheck all checkboxes
        for checkbutton_var in self.checkbuttons_var:
            checkbutton_var.set(False)


if __name__ == "__main__":
    app = Window()
    app.mainloop()
