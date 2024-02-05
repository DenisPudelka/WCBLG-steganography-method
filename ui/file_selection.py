import tkinter as tk
from tkinter import filedialog, messagebox

class FileSelectionUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.initWidgets()

    def initWidgets(self):
        tk.Button(self, text="Select File", command=self.select_file).grid(row=8, column=0)
        self.file_label = tk.Label(self, text="No file selected")
        self.file_label.grid(row=8, column=1)

        self.status_label = tk.Label(self, text="")
        self.status_label.grid(row=10, column=0, columnspan=2)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_label.config(text=file_path)