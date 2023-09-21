import logging
# -*- coding: utf-8 -*-
"""
Created on 2021-11-13

@author: rfwebster
"""

import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox

from ui.elogger import Ui_MainWindow
from datetime import datetime
import csv


import math

LOG_FILE = 'C:\Data\logger\log.csv'

_status = 0  # online
try:
    from PyJEM import detector, TEM3
    TEM3.connect()
except(ImportError):
    from PyJEM.offline import detector, TEM3
    _status = 1  # offline

LOG_FILE = "C:\Data\logger\log.csv"


class Window(QMainWindow, Ui_MainWindow):
    '''
    The Window class provides the main functionalities of the Flash Logger application. It allows the user to input their name, select whether a sample is in and whether liquid nitrogen is filled, select the type of flash, add notes, and log the data to a CSV file. It also displays the date and time of the last entry in the CSV file.

    Methods:
    - update_text_labels(): Updates the date and time and flash type labels based on the last entry in the CSV file.
    - check_file_exists(): Checks if the CSV file exists and creates it with a header row if it doesn't.
    - read_last_line(): Reads the last line of the CSV file and returns it as a list.
    - add_line_to_csv(): Adds a new line to the CSV file with the current date and time, user name, sample in and LN2 filled status, HT, EC, A1, A2, flash type, and notes.
    - go(): Retrieves the current values of the user input fields and adds a new line to the CSV file using add_line_to_csv(), then resets the input fields.
    - reset(): Clears the user input fields and unchecks the sample in and LN2 filled checkboxes.
    - uncheck_all_checkboxes(): Unchecks all checkboxes in the checkboxes list.

    Fields:
    - checkboxes: A list containing the sample in and LN2 filled checkboxes.
    - previousentry: The last entry in the CSV file as a list.
    - datetime: The current date and time as a string.
    - ht: The current HT value as an integer.
    - EC: The current emission current value as an integer.
    - A1: The current anode 1 current value as an integer.
    - A2: The current anode 2 current value as an integer.
    - user: The current user name as a string.
    - flashtype: The current flash type as a string.
    - notes: The current notes as a string.
    '''
    csv_header = ["datetime", "user",
            "Sample in?", "LN2 Filled?",
            "SIP 1", "SIP 2", "SIP 200", "SIP 3",
            "HT", "EC",
            "A1", "A2",
            "Flash Type",
            "Notes"]
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.startButton.clicked.connect(self.go)

        self.lens = TEM3.Lens3()
        self.deflector = TEM3.Def3()
        self.eos = TEM3.EOS3()
        self.det = TEM3.Detector3()
        self.apt = TEM3.Apt3()
        self.HT = TEM3.HT3()
        self.gun = TEM3.GUN3()
        self.checkboxes = [checkbox for checkbox in self.findChildren(QCheckBox)]

        self.check_file_exists(LOG_FILE)
        self.update_text_labels()


    def update_text_labels(self):
        self.previousentry = self.read_last_line(LOG_FILE)
        if self.previousentry is not None:
            self.datetime_label.setText(self.previousentry[0])
            self.flash_label.setText(self.previousentry[12])

    def check_file_exists(self, file_path):
        if not os.path.exists(file_path):
            directory, filename = os.path.split(file_path)
            os.makedirs(directory)
            with open(file_path, "w", newline="", encoding="utf-8") as f:

                writer = csv.writer(f)
                writer.writerow(self.csv_header)

    def read_last_line(self, file_path):
        if not os.path.exists(file_path):
            directory, filename = os.path.split(file_path)
            os.makedirs(directory)
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.csv_header)

            logging.error("Please close the .csv file and restart the program")
            self.statusBar.showMessage("Please close the csv file and restart the program")
            return None

        try:
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                lines = f.readlines()
                last_line = lines[-1].strip().split(',') if len(lines) > 0 else None
                return last_line

        except PermissionError:
            logging.error("Please close the .csv file and restart the program")
            self.statusBar.showMessage("Please close the csv file and restart the program")
            return None

    def add_line_to_csv(self, file_path, variables):
        try:
            with open(file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(variables)
        except PermissionError:
            logging.error("Please close the .csv file and restart the program")
            self.statusBar.showMessage("Please close the csv file and restart the program")

    def go(self):
        self.datetime = datetime.now()
        self.datetime = self.datetime.strftime("%Y-%m-%d %H:%M")
        self.ht = self.HT.GetHtValue()
        self.EC = self.gun.GetEmissionCurrentValue()
        self.A1 = self.gun.GetAnode1CurrentValue()
        self.A2 = self.gun.GetAnode2CurrentValue()
        self.user = self.useredit.text()
        self.flashtype = self.comboBox.currentText()
        self.notes = self.notebox.toPlainText()
        self.samplein = self.sample_checkBox.isChecked()
        self.ln2 = self.ln2_checkBox.isChecked()
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
        self.useredit.setText("")
        self.notebox.clear()
        self.uncheck_all_checkboxes()
        self.update_text_labels()


    def uncheck_all_checkboxes(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    win = Window()
    win.show()
    sys.exit(app.exec())