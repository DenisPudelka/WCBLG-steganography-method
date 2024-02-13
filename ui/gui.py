import tkinter as tk
from tkinter import *
from ui.embed import EmbedMode

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Steganography Application")
        self.init_widgets()

    def init_widgets(self):
        self.resizable(False,False)
        self.main_freme = tk.LabelFrame(self, text="Steganography Mode", padx=50, pady=50)
        self.main_freme.pack(padx=40, pady=40)

        self.embed_button_mode = tk.Button(self.main_freme, text="Embed Mode", command=self.open_embed_window)
        self.embed_button_mode.pack(side=tk.LEFT, padx=10, pady=10)

        self.extract_button_mode = tk.Button(self.main_freme, text="Extract Mode")
        self.extract_button_mode.pack(side=tk.RIGHT, padx=10, pady=10)

    def open_embed_window(self):
        EmbedMode()

    def open_extract_window(self):
        pass