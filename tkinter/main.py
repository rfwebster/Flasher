import tkinter as tk
from tkinter import ttk
import tkinter.font as font
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
    def setup_ui(self):


        PAD_X = 10
        PAD_Y = 10

        self.title("Flash Logger!")
        self.geometry("350x450")
        self.resizable(0, 0)

        self.frame1 = tk.Frame(self)
        self.frame1.pack(fill=tk.X)
        
        self.user_label = ttk.Label(self.frame1, text="User Name:", width=10)
        self.user_label.pack(side=tk.LEFT, padx=PAD_X, pady=PAD_Y, )

        self.user_edit = ttk.Entry(self.frame1)
        self.set_user_text("")
        self.user_edit.bind("<FocusIn>", self.clear_user_text)
        self.user_edit.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y, expand=True)

        self.frame2 = tk.Frame(self)
        self.frame2.pack(fill=tk.X)        
        self.flash_label = ttk.Label(self.frame2, text="Flash Type:", width=10)
        self.flash_label.pack(side=tk.LEFT, padx=PAD_X, pady=PAD_Y, )
        self.comboBox = ttk.Combobox(self.frame2, values=["High Flash", "Low Flash"], state="readonly")
        self.comboBox.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y, expand=True)
       
        self.frame3 = tk.Frame(self)
        self.frame3.pack(fill=tk.X)  
        self.flash_label = ttk.Label(self.frame3, text="Liquid N2:", width=10)
        self.flash_label.pack(side=tk.LEFT, padx=PAD_X, pady=PAD_Y, )

        self.ln2_checkbutton_var = tk.BooleanVar()
        self.ln2_checkbutton = ttk.Checkbutton(self.frame3, text="Filled", variable=self.ln2_checkbutton_var)
        self.ln2_checkbutton.pack(padx=PAD_X, pady=PAD_Y)
        self.checkbuttons_var.append(self.ln2_checkbutton_var)


        self.notebox = tk.Text(self, height=5, width=40)
        self.set_notebox_text()
        self.notebox.bind("<FocusIn>", self.clear_notebox_text)

        self.notebox.pack(padx=PAD_X, pady=PAD_Y)

        self.startButton = ttk.Button(self, text="Log!", command=self.go)
        self.startButton.pack(padx=PAD_X, pady=PAD_Y)




        self.groupBox = ttk.LabelFrame(self, text="Last Flash:")
        self.groupBox.pack(padx=PAD_X, pady=PAD_Y)

        self.formLayoutWidget = tk.Frame(self.groupBox)
        self.formLayoutWidget.pack(padx=PAD_X, pady=PAD_Y)

        self.label = ttk.Label(self.formLayoutWidget, text="Date/Time:")
        self.label.grid(row=0, column=0, sticky=tk.E, padx=PAD_X)

        self.datetime_label = ttk.Label(self.formLayoutWidget, text="yyyy/mm/dd 00:00")
        self.datetime_label.grid(row=0, column=1, sticky=tk.W, padx=PAD_X)

        self.label_2 = ttk.Label(self.formLayoutWidget, text="Type:")
        self.label_2.grid(row=1, column=0, sticky=tk.E, padx=PAD_X)

        self.flash_label = ttk.Label(self.formLayoutWidget, text="High Flash")
        self.flash_label.grid(row=1, column=1, sticky=tk.W, padx=PAD_X)

        self.EC_label = ttk.Label(self.formLayoutWidget, text="Emission Value =")
        self.EC_label.grid(row=2, column=0, sticky=tk.E, padx=PAD_X)

        self.EC_Val__label = ttk.Label(self.formLayoutWidget, text=f"{self.gun.GetEmissionCurrentValue()}uA")
        self.EC_Val__label.grid(row=2, column=1, sticky=tk.W, padx=PAD_X)

        self.instruction_label = ttk.Label(self.formLayoutWidget, text="Do a low flash.")
        self.instruction_label.grid(row=3, column=0, columnspan=2, padx=PAD_X)

        self.status_bar = ttk.Label(self, text="", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        

    def old_setup_ui(self):

        normal_fonts = font.Font(family='Helvetica', size=12)
        bold_fonts = font.Font(family='Helvetica', size=12, weight='bold')

        style = ttk.Style()
        # style.theme_use('clam')  # Choose a built-in theme (you can try different themes)

        # Customize the appearance
        self.configure(bg='darkgrey')
        # style.configure('.', background='darkgrey')
        style.configure('TLabel', font=normal_fonts, justify="left", anchor="w")
        style.configure('TButton', highlightbackground='green', bg='lightgreen', fg='green', font=normal_fonts)
        style.configure('TEntry', fieldbackground='white', font=normal_fonts)
        style.configure('TSpinbox', fieldbackground='white', font=normal_fonts)
        style.configure('TCombobox', fieldbackground='white', font=normal_fonts)
        style.configure('Horizontal.TProgressbar', bg='lightgreen')

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

        self.user_edit = ttk.Entry(self.gridLayoutWidget)
        self.set_user_text("")
        self.user_edit.bind("<FocusIn>", self.clear_user_text    )
        self.user_edit.grid(row=0, column=0, pady=PAD_Y)

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

        self.EC_label = ttk.Label(self.formLayoutWidget, text="Emission Value =")
        self.EC_label.grid(row=2, column=0, padx=PAD_X)

        self.EC_Val__label = ttk.Label(self.formLayoutWidget, text=f"{self.gun.GetEmissionCurrentValue()}uA")
        self.EC_Val__label.grid(row=2, column=1, padx=PAD_X)

        self.instruction_label = ttk.Label(self.formLayoutWidget, text="Do a low flash.", font=bold_fonts)
        self.instruction_label .grid(row=3, column=0, columnspan=2, padx=PAD_X)

        self.status_bar = ttk.Label(self, text="", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.set_status("Welcome to the Emission Logger!")

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


    def update_instruction_label(self, txt):
        self.instruction_label.config(text=txt)

    def update_text_labels(self):
        # Method to update the date and time and flash type labels
        # based on the last entry in the CSV file
        self.previousentry = self.read_last_line(LOG_FILE)
        if self.previousentry is not None:
            print(self.previousentry)
            #print(self.previousentry[0], self.previousentry[12])
            self.datetime_label.config(text=self.previousentry[0])
            #self.flash_label.config(text=self.previousentry[12])
        self.update_instruction_label(self.get_flash_type())


    def go(self):
    #     # Method to retrieve the current values of the user input fields
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

        if last_entry is not None:
            last_entry_time_str = last_entry[0]
            last_entry_time = datetime.strptime(last_entry_time_str, "%Y-%m-%d %H:%M")
            current_time = datetime.now()

            # Check if the time of the last entry is from the same calendar day as the current time
            if last_entry_time.date() == current_time.date():
                # Check if the emission value is above 12
                if float(last_entry[10]) > 12.0:  # Assuming emission value is in column index 10
                    flash_type = "none"
                # Check if the emission value is below 12
                elif float(last_entry[10]) < 12.0:  # Assuming emission value is in column index 10
                    flash_type = "low"
                else:
                    flash_type = "high"  # If the emission value is exactly 12, do a high flash
            else:
                flash_type = "high"  # If the times are not from the same day, do a high flash
        else:
            flash_type = "high"  # If there is no previous entry, do a high flash by default

        # Use case statements to determine the flash type label
        flash_type_label = {
            "none": "Do nothing",
            "low": "Do a low flash",
            "high": "Do a high flash"
        }.get(flash_type, "Do a high flash")

        return flash_type_label



    def reset(self):
        # implementation to clear the user input fields and uncheck the checkboxes
        self.uncheck_all_checkbuttons()
        self.update_text_labels()
        self.set_notebox_text()
        self.set_user_text("User Name")
        return 0
    
    def uncheck_all_checkbuttons(self):
        # implementation to uncheck all checkboxes
        for checkbutton_var in self.checkbuttons_var:
            checkbutton_var.set(False)


if __name__ == "__main__":
    app = Window()
    app.mainloop()
