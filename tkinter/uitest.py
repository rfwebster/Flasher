import tkinter as tk
from tkinter import ttk
from tkinter import font

class FlasherApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        self.title("Flasher!")
        self.geometry("400x350")
        self.resizable(0, 0)

        # Create a ttk style object
        s = ttk.Style()
        s.theme_use('default')

        # Define a color palette
        background_color = "#f2f2f2"
        primary_color = "#3498db"
        secondary_color = "#e74c3c"

        # Configure styles
        s.configure('TLabel', background=background_color, font=('Roboto', 12))
        s.configure('TButton', foreground='white', font=('Roboto', 12))

        # Create frames
        self.mainframe = ttk.Frame(self, padding=10)
        self.mainframe.pack(fill=tk.BOTH, expand=True)

        self.user_frame = ttk.Frame(self.mainframe)
        self.user_frame.pack(fill=tk.X, padx=10, pady=(10, 0), ipady=5)

        # Create and configure widgets
        self.user_label = ttk.Label(self.user_frame, text="User Name:")
        self.user_label.pack(side=tk.LEFT)

        self.user_edit = ttk.Entry(self.user_frame)
        self.set_user_text("")
        self.user_edit.bind("<FocusIn>", self.clear_user_text)
        self.user_edit.pack(fill=tk.BOTH, expand=True)

        # Add additional widgets and styling here...

        self.startButton = ttk.Button(self.mainframe, text="Log!", style='TButton')
        self.startButton.pack(fill=tk.BOTH, padx=10, pady=10)

        # Status bar
        self.status_bar = ttk.Label(self, text="", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_user_text(self, text):
        self.user_edit.delete(0, tk.END)
        self.user_edit.insert(0, text)

    def clear_user_text(self, event):
        if self.user_edit.get() == "Enter User":
            self.user_edit.delete(0, tk.END)

    def go(self):
        # Add functionality for the "Log!" button
        pass

if __name__ == "__main__":
    app = FlasherApp()
    app.mainloop()

