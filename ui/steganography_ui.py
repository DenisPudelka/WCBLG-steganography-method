import tkinter as tk
from tkinter import filedialog, messagebox

from ui.algorithm_parameters import *
from ui.file_selection import *

class Steganography_UI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.init_widgets()

    def init_widgets(self):
        self.title("Steganography Program")

        self.parameters_ui = AlgorithmParameterUI(self)
        self.parameters_ui.pack(fill='both', expand=True)

        self.file_ui = FileSelectionUI(self)
        self.file_ui.pack(fill='x', expand=True)

        tk.Button(self, text="Embed").pack(side='left')
        tk.Button(self, text="Extract").pack(side='right')

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_label.config(text=file_path)