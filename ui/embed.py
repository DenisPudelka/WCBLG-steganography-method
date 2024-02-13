import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import *


class EmbedMode:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.geometry("350x700")
        self.window.resizable(False, False)
        self.window.title("Embed Mode")
        self.init_widgets()

    def init_widgets(self):
        self.window_frame = tk.LabelFrame(self.window, text="Embedding Mode")
        self.window_frame.pack(fill="both", expand=True, padx=15, pady=15)
        self.parameter_frame_widgets()
        self.transformation_frame_widgets()
        self.input_files_frame()
        self.execute_btn = tk.Button(self.window_frame, text="Execute")
        self.execute_btn.pack(padx=10, pady=10)

    def parameter_frame_widgets(self):
        self.parameters_frame = tk.LabelFrame(self.window_frame)
        self.parameters_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(self.parameters_frame, text="Parameters", font=("Helvetica", 10)).grid(row=0, column=0, columnspan=2,
                                                                                        pady=10)

        tk.Label(self.parameters_frame, text="Key: ").grid(row=1, column=0, sticky="e")
        self.key_entry = tk.Entry(self.parameters_frame)
        self.key_entry.grid(row=1, column=1, sticky="w", pady=5)
        self.key_entry.insert(0, "e.g., 12345")

        tk.Label(self.parameters_frame, text="Block Size (Bs): ").grid(row=2, column=0, sticky="e")
        self.bs_entry = tk.Entry(self.parameters_frame)
        self.bs_entry.grid(row=2, column=1, sticky="w", pady=5)
        self.bs_entry.insert(0, "e.g., 256")

        tk.Label(self.parameters_frame, text="Multiplier (Mul): ").grid(row=3, column=0, sticky="e")
        self.mul_entry = tk.Entry(self.parameters_frame)
        self.mul_entry.grid(row=3, column=1, sticky="w", pady=5)
        self.mul_entry.insert(0, "e.g., 1.2")

        tk.Label(self.parameters_frame, text="Population Size (Npop): ").grid(row=4, column=0, sticky="e")
        self.pop_size_entry = tk.Entry(self.parameters_frame)
        self.pop_size_entry.grid(row=4, column=1, sticky="w", pady=5)
        self.pop_size_entry.insert(0, "e.g., 50")

        tk.Label(self.parameters_frame, text="Population Size (Npop): ").grid(row=5, column=0, sticky="e")
        self.pop_size_entry = tk.Entry(self.parameters_frame)
        self.pop_size_entry.grid(row=5, column=1, sticky="w", pady=5)
        self.pop_size_entry.insert(0, "e.g., 50")

        tk.Label(self.parameters_frame, text="Crossover (Pc): ").grid(row=6, column=0, sticky="e")
        self.crossover_entry = tk.Entry(self.parameters_frame)
        self.crossover_entry.grid(row=6, column=1, sticky="w", pady=5)
        self.crossover_entry.insert(0, "e.g., 0.7")

        tk.Label(self.parameters_frame, text="Mutation (Pm): ").grid(row=7, column=0, sticky="e")
        self.mutation_entry = tk.Entry(self.parameters_frame)
        self.mutation_entry.grid(row=7, column=1, sticky="w", pady=5)
        self.mutation_entry.insert(0, "e.g., 0.2")

        tk.Label(self.parameters_frame, text="Epoch: ").grid(row=8, column=0, sticky="e")
        self.epoch_entry = tk.Entry(self.parameters_frame)
        self.epoch_entry.grid(row=8, column=1, sticky="w", pady=5)
        self.epoch_entry.insert(0, "e.g., 20")

    def transformation_frame_widgets(self):
        self.transformation_frame = tk.LabelFrame(self.window_frame)
        self.transformation_frame.pack(fill="both", expand=True, padx=10, pady=10)

        label = tk.Label(self.transformation_frame, text="Choose transformation method", font=("Helvetica", 10))
        label.pack(pady=10)

        radio_button_frame = tk.Frame(self.transformation_frame)
        radio_button_frame.pack(pady=10)

        self.dwt_radio_button = tk.Radiobutton(radio_button_frame, text="DWT")
        self.dwt_radio_button.pack(side="left", expand=True)

        self.iwt_radio_button = tk.Radiobutton(radio_button_frame, text="IWT")
        self.iwt_radio_button.pack(side="left", expand=True)

    def input_files_frame(self):
        self.file_frame = tk.LabelFrame(self.window_frame)
        self.file_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(self.file_frame, text="File inputs", font=("Helvetica", 10)).pack(pady=10)

        image_frame = tk.Frame(self.file_frame)
        image_frame.pack(fill="x", pady=5)

        tk.Label(image_frame, text="Image:").pack(side="left")
        tk.Button(image_frame, text="Select File", command=self.select_file).pack(side="left", padx=10)
        self.image_file_label = tk.Label(image_frame, text="No file selected")
        self.image_file_label.pack(side="left")

        message_frame = tk.Frame(self.file_frame)
        message_frame.pack(fill="x", pady=5)

        tk.Label(message_frame, text="Message:").pack(side="left")
        tk.Button(message_frame, text="Select File", command=self.select_file).pack(side="left", padx=10)
        self.message_file_label = tk.Label(message_frame, text="No file selected")
        self.message_file_label.pack(side="left")

    def select_file(self):
        file_path = tk.filedialog.askopenfilename()
        if file_path:
            self.file_label.config(text=file_path)
