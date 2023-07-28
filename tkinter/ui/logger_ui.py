import tkinter as tk
from tkinter import ttk

class Ui_MainWindow:
    def __init__(self, MainWindow):
        MainWindow.title("Flash Logger!")
        MainWindow.geometry("412x460")

        self.centralwidget = tk.Frame(MainWindow)
        self.centralwidget.pack(fill=tk.BOTH, expand=True)

        self.gridLayoutWidget = tk.Frame(self.centralwidget)
        self.gridLayoutWidget.pack(padx=10, pady=20)

        self.comboBox = ttk.Combobox(self.gridLayoutWidget, values=["High Flash", "Low Flash"], state="readonly")
        self.comboBox.grid(row=3, column=0, pady=10)

        self.notebox = tk.Text(self.gridLayoutWidget, height=5)
        self.notebox.grid(row=4, column=0, pady=10)

        self.startButton = ttk.Button(self.gridLayoutWidget, text="Log!", command=self.go)
        self.startButton.grid(row=5, column=0, pady=10)

        self.sample_checkBox = ttk.Checkbutton(self.gridLayoutWidget, text="Sample In")
        self.sample_checkBox.grid(row=1, column=0, pady=10)

        self.useredit = ttk.Entry(self.gridLayoutWidget)
        self.useredit.grid(row=0, column=0, pady=10)

        self.ln2_checkBox = ttk.Checkbutton(self.gridLayoutWidget, text="Liquid Nitrogen Filled")
        self.ln2_checkBox.grid(row=2, column=0, pady=10)

        self.groupBox = ttk.LabelFrame(self.centralwidget, text="Last Flash:")
        self.groupBox.pack(padx=10, pady=10)

        self.formLayoutWidget = tk.Frame(self.groupBox)
        self.formLayoutWidget.pack(padx=10, pady=10)

        self.label = ttk.Label(self.formLayoutWidget, text="Date/Time:")
        self.label.grid(row=0, column=0, padx=10)

        self.datetime_label = ttk.Label(self.formLayoutWidget, text="yyyy/mm/dd 00:00")
        self.datetime_label.grid(row=0, column=1, padx=10)

        self.label_2 = ttk.Label(self.formLayoutWidget, text="Type:")
        self.label_2.grid(row=1, column=0, padx=10)

        self.flash_label = ttk.Label(self.formLayoutWidget, text="High Flash")
        self.flash_label.grid(row=1, column=1, padx=10)

    def go(self):
        # Your logic to handle the "Log!" button click goes here

if __name__ == "__main__":
    root = tk.Tk()
    app = Ui_MainWindow(root)
    root.mainloop()
