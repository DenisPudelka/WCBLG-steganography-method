import tkinter as tk
from tkinter import *
from ui.embed import EmbedMode  # Impoerting EmbedMode class
from ui.extract import ExtractMode  # Importing ExtractMode class

class GUI(tk.Tk):
    def __init__(self, eng):
        ''' Initialize the main GUI window with an engine parameter and set up the window's properties and widgets.'''
        super().__init__()
        self.eng = eng
        self.title("Steganography Application")
        self.init_widgets()

    def init_widgets(self):
        """
        Set up the widgets in the main application window, including buttons to access embedding and extraction modes.
        """
        self.resizable(False, False)
        self.main_freme = tk.LabelFrame(self, text="Steganography Mode", padx=25, pady=25)
        self.main_freme.pack(padx=10, pady=10)

        self.embed_button_mode = tk.Button(self.main_freme, text="Embed Mode", command=self.open_embed_window)
        self.embed_button_mode.pack(side=tk.LEFT, padx=10, pady=10)

        self.extract_button_mode = tk.Button(self.main_freme, text="Extract Mode", command=self.open_extract_window)
        self.extract_button_mode.pack(side=tk.RIGHT, padx=10, pady=10)

    def open_embed_window(self):
        """Open the embedding mode window."""
        EmbedMode(self.eng)

    def open_extract_window(self):
        """Open the extraction mode window."""
        ExtractMode(self.eng)