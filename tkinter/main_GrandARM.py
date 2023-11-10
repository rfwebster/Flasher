import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from datetime import datetime
import csv
import os


LOG_FILE = 'C:/Data/flasher/log.csv'

_status = 0  # online
try:
    from PyJEM import detector, TEM3
    TEM3.connect()
except ImportError:
    from PyJEM.offline import detector, TEM3
    _status = 1  # offline

LOG_FILE = "C:/Data/flasher/log.csv"


class Window(tk.Tk):
    checkbuttons_var = []

    HT = TEM3.HT3()
    gun = TEM3.GUN3()
    feg = TEM3.FEG3()
    stage = TEM3.Stage3()

    current_emission = 12

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
        # self.protocol("WM_DELETE_WINDOW", self.disable_close)

        self.setup_ui()
        self.check_file_exists(LOG_FILE)
        
        self.update_text_labels()

        self.current_emission = self.get_emission()
        self.last_flash_type = "unknown"

        # Schedule a UI update
        self.schedule_ui_refresh()

    def schedule_ui_refresh(self):
        # Schedule the refresh_ui method to run every 30 seconds
        self.after(30000, self.refresh_ui)

    def refresh_ui(self):
        
        self.get_emission()
        self.get_last_flash_type()

        self.update_text_labels()
        self.set_status_bar_text()

        # Schedule the next UI refresh
        self.schedule_ui_refresh()

    def disable_close(self):
        pass

    def setup_ui(self):
        #photo = tk.PhotoImage(file = "tkinter/ui/icon.ico")
        #self.iconphoto(False, photo)
        
        s = ttk.Style()

        PAD_X = 10
        PAD_Y = 5

        self.title("Flasher!")
        #self.geometry("350x400")
        #self.resizable(0, 0)

        # Create new font objects with the desired font sizes and fonts
        label_font = font.Font(family="Arial", size=11)
        flash_font = ('Comic Sans MS', 14)
        flash_font2 =  ('Comic Sans MS', 11)
        log_button_font = ('Comic Sans MS', 28, 'bold')

        # configure styes
        s.configure('TLabel', foreground='black', font=label_font)
        s.configure('log.TButton',  foreground='black', font=log_button_font)
        s.configure('low_flash.TLabel', background='orange', foreground='black', font=flash_font)
        s.configure('low_flash2.TLabel', background='orange', foreground='black', font=flash_font2)
        s.configure('high_flash.TLabel', background='yellow', foreground='black', font=flash_font)
        s.configure('no_flash.TLabel', background='green', foreground='black', font=flash_font)
        s.configure('unknown_flash.TLabel', background='red', foreground='black', font=flash_font)


        self.mainframe = tk.Frame(self)
        self.mainframe.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)

        self.instructions_frame = tk.LabelFrame(self.mainframe, text="Instructions:")
        self.instructions_frame.pack(fill=tk.X)
        Instructions = "Use this window to log each time you do a flash. \n" +\
        "1. Perform the flash and turn on the emission. \n" +\
        "2. Wait for the values to stabalise. \n" +\
        "3. Fill in the details below and click \"Log it!\" \n\n" +\
        "If any of the values are quite different, please contact a member of EMU staff."        
        

        self.label = ttk.Label(self.instructions_frame, text=Instructions, wraplength=400, font=label_font)
        self.label.pack(fill=tk.X, padx=PAD_X)

        self.instruction_label = ttk.Label(self.instructions_frame  , text="Unknown State :`(", style='unknown.TLabel')
        self.instruction_label.pack(fill='both', padx=PAD_X, pady=PAD_Y, ipadx=PAD_X, ipady=PAD_Y)



        self.user_frame = tk.LabelFrame(self.mainframe, text="Fill:")
        self.user_frame.pack(fill=tk.X)

        
        self.frame1 = tk.Frame(self.user_frame)
        self.frame1.pack(fill=tk.X)
        
        self.user_label = ttk.Label(self.frame1, text="User Name:", width=10)
        self.user_label.pack(side=tk.LEFT, padx=PAD_X, pady=PAD_Y, )

        self.user_edit = ttk.Entry(self.frame1, font=label_font)
        self.set_user_text("")
        self.user_edit.bind("<FocusIn>", self.clear_user_text)
        self.user_edit.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y, expand=True)

        self.frame2 = tk.Frame(self.user_frame)
        self.frame2.pack(fill=tk.X)        
        self.flash_label = ttk.Label(self.frame2, text="Flash Type:", width=10)
        self.flash_label.pack(side=tk.LEFT, padx=PAD_X, pady=PAD_Y)
        self.comboBox = ttk.Combobox(self.frame2, values=["High Flash", "Low Flash", "No Flash"], state="readonly", font=label_font)
        self.comboBox.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y, expand=True)
        self.comboBox.current(0)
       
        self.frame3 = tk.Frame(self.user_frame)
        self.frame3.pack(fill=tk.X)  
        self.flash_label = ttk.Label(self.frame3, text="Liquid N2:", width=10)
        self.flash_label.pack(side=tk.LEFT, padx=PAD_X, pady=PAD_Y, )

        self.ln2_checkbutton_var = tk.BooleanVar()
        self.ln2_checkbutton = tk.Checkbutton(self.frame3, text="Filled", variable=self.ln2_checkbutton_var,
                                              font=label_font)
        self.ln2_checkbutton.pack(padx=PAD_X, pady=PAD_Y)
        self.checkbuttons_var.append(self.ln2_checkbutton_var)

        self.notebox = tk.Text(self.user_frame, height=5, width=40, font=label_font)
        self.set_notebox_text()
        self.notebox.bind("<FocusIn>", self.clear_notebox_text)
        self.notebox.pack(padx=PAD_X, pady=PAD_Y)

        self.vac_frame = tk.LabelFrame(self.mainframe, text="Vacuum:")
        self.vac_frame.pack(fill=tk.X)
        self.vac_label = ttk.Label(self.vac_frame, text="Vacuum:", width=10)
        self.vac_label.grid(row=0, column=0, padx=PAD_X, pady=PAD_Y, sticky=tk.W)

        self.PiGRT_label = ttk.Label(self.vac_frame, text="RT (PiG):", width=20)
        self.PiGRT_label.grid(row=1, column=0, padx=PAD_X, pady=PAD_Y, sticky=tk.W)
        self.PiGRTvar = tk.StringVar(value="42")
        self.PiGRT_spin = ttk.Spinbox(self.vac_frame, from_=0, to=255, increment=1, width=4, font=label_font, textvariable=self.PiGRTvar)
        self.PiGRT_spin.grid(row=1, column=1, sticky=tk.E)
        self.PiGRTunit_label = ttk.Label(self.vac_frame, text="uA", width=4)
        self.PiGRTunit_label.grid(row=1, column=4, sticky=tk.E)

        self.SIP3_label = ttk.Label(self.vac_frame, text="Column:", width=20)
        self.SIP3_label.grid(row=2, column=0, padx=PAD_X, pady=PAD_Y, sticky=tk.W)
        self.SIP3var = tk.StringVar(value="8.1")
        self.SIP3_spin = ttk.Spinbox(self.vac_frame, from_=0, to=10, increment=0.1, width=4, font=label_font, textvariable=self.SIP3var)
        self.SIP3_spin.grid(row=2, column=1, sticky=tk.E)
        self.SIP3exp_label = ttk.Label(self.vac_frame, text="x10^", width=4)
        self.SIP3exp_label.grid(row=2, column=2, sticky=tk.E)
        self.SIP3expvar = tk.StringVar(value="-6")
        self.SIP3exp_spin = ttk.Spinbox(self.vac_frame, from_=-9, to=-3, increment=1, width=2, font=label_font, textvariable=self.SIP3expvar)
        self.SIP3exp_spin.grid(row=2, column=3,sticky=tk.E)
        self.SIP3unit_label = ttk.Label(self.vac_frame, text="Pa", width=4)
        self.SIP3unit_label.grid(row=2, column=4, sticky=tk.E)



        self.startButton = ttk.Button(self.mainframe, text="Log it!", command=self.logit, style='log.TButton')
        self.startButton.pack(fill='both', padx=PAD_X, pady=2*PAD_Y)

        #progress bar
        self.status_bar = ttk.Label(self, text="", relief=tk.FLAT, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        
    def set_status_bar_text(self):
        self.status_bar.config(text="Emission: {:.2f}uA \t Last flash: {}".format(self.current_emission,
                                                                        self.last_flash_type))

    def clear_user_text(self, e):
        self.user_edit.delete(0,tk.END)
    
    def set_user_text(self, text):
        self.user_edit.delete(0,tk.END)
        self.user_edit.insert(tk.END, text)

    def get_user_text(self):
        text_content = self.user_edit.get()
        text_content = text_content.replace("\n", "")  # Remove newlines
        return text_content
    
    def get_vac_values(self):
        self.PiG = self.PiGRTvar.get()

        self.SIP3var = self.SIP3_spin.get()
        self.SIP3expvar = self.SIP3exp_spin.get()
        self.SIP3 = self.SIP3var + "E" + self.SIP3expvar

    def get_last_vac_values(self):
        last_entry = self.read_last_line(LOG_FILE)
        if last_entry:
            self.PiG = last_entry[6]
            self.SIP3 = last_entry[7]
        else:
            self.PiG = "40"
            self.SIP3 = "8.1E-6"

    def set_vac_values(self):
        self.get_last_vac_values()
        
        self.PiGRT_spin.delete(0,tk.END)
        self.PiGRT_spin.insert(tk.END, self.PiG)


        self.SIP3_spin.delete(0,tk.END)
        self.SIP3_spin.insert(tk.END, self.SIP3.split("E")[0])
        self.SIP3exp_spin.delete(0,tk.END)
        self.SIP3exp_spin.insert(tk.END, self.SIP3.split("E")[1])


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
            print("Please close the csv file and restart the program")
            return None
        
        try:
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                lines = f.readlines()[1:]
                last_line = lines[-1].strip().split(',') if len(lines) > 0 else None
                return last_line

        except PermissionError:
            print("Please close the csv file and restart the program")
            return None
        
    def add_line_to_csv(self, file_path, variables):
        # implementation to add a new line to the CSV file with the given data
        try:
            with open(file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(variables)
        except PermissionError: 
            #logging.error("Please close the .csv file and restart the program")
            self.print("Please close the csv file and restart the program")


    def update_instruction_label(self, _status):
        if _status == 0:
            self.instruction_label.config(text="No Action Required", style='no_flash.TLabel')
            self.comboBox.current(2)
        elif _status == 1:
            self.instruction_label.config(text="Do a High Flash", style='high_flash.TLabel')
            self.comboBox.current(0)
        elif _status == 2:
            self.instruction_label.config(text="Do a Low Flash", style='low_flash.TLabel')
            self.comboBox.current(1)
        elif _status == 3:
            self.instruction_label.config(text="Turn emission off then Low Flash", style='low_flash2.TLabel')
            self.comboBox.current(1)
        else:
            self.instruction_label.config(text="Unknown status :\'(", style='unknown_flash.TLabel')
            self.comboBox.current(2)
            

    def update_text_labels(self):
        # Method to update the date and time and flash type labels
        # based on the last entry in the CSV file
        self.previousentry = self.read_last_line(LOG_FILE)
        if self.previousentry is not None:
            flash_type = self.get_flash_type()
            self.update_instruction_label(flash_type)
            self.set_vac_values()


    def get_emission(self):
        self.current_emission = self.gun.GetEmissionCurrentValue()
        return self.current_emission
    

    def get_last_flash_type(self):
        self.last_flash_type = self.read_last_line(LOG_FILE)[-2]
        return self.last_flash_type

    def logit(self):
        # Logs the flash just done  Method to retrieve the current values of the user input fields
        # and add a new line to the CSV file using add_line_to_csv, then reset the input fields
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
        self.get_vac_values()
        self.add_line_to_csv(LOG_FILE, [
            self.datetime, self.user,
            self.samplein, self.ln2,
            "SIP1", "SIP2", str(self.PiG), str(self.SIP3),
            self.ht, self.EC,
            self.A1, self.A2,
            self.flashtype,
            self.notes]
        )
        self.reset()


    def get_flash_type(self):
        # determines what the next flash should be high or low based on logic 

        last_flash_time  = self.get_last_flash_time()
        current_time = datetime.now()
        self.get_emission()
    
        if self.current_emission == 0.0:
            # Emission is off
            if last_flash_time.date() != current_time.date():
                # Last flash wasn't today
                return 1  # Do a high flash
            else:
                return 2  # Do a low flash
        elif 0.0 < self.current_emission <= 12.0:
            # Emission is between 0 and 12
            return 3  # Turn the emission off and do a low flash
        elif self.current_emission > 12.0:
            # Emission is on and above 12
            time_since_last_flash = (current_time - last_flash_time).total_seconds()
            if time_since_last_flash >= 4 * 60 * 60:
                # Last flash was more than 4 hours ago
                return 3  # Turn the emission off and do a low flash
            else:
                return 0  # Do nothing
        else:
            return 4  # Unknown state


    def uncheck_all_checkbuttons(self):
        # implementation to uncheck all checkboxes
        for checkbutton_var in self.checkbuttons_var:
            checkbutton_var.set(False)

    def reset(self):
        # implementation to clear the user input fields and uncheck the checkboxes
        self.uncheck_all_checkbuttons()
        self.update_text_labels()
        self.set_notebox_text()
        self.set_vac_values()
        self.set_user_text(" ")
        self.set_status_bar_text()
        return 0
    


if __name__ == "__main__":
    app = Window()
    app.mainloop()
