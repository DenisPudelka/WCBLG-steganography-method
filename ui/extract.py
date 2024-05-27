import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from stego.Utils import *   # Utility functions for steganography
from stego.WCBLGExtraction_version_2 import WCBLGExtraction # Extraction algorithm
import tifffile # For reading TIFF files
import threading


class ExtractMode:
    def __init__(self, eng):
        """Initialize the extraction GUI with a reference to an engine and default values."""
        self.eng = eng  # Engine used for MATLAB
        self.image_path = ''
        self.bestSeeds_path = ''
        self.extracting_params = None
        self.window = tk.Toplevel()
        self.window.geometry("500x500")
        self.window.resizable(False, False)
        self.window.title("Extract Mode")
        self.init_widgets() # Initializing the widgets inside the window

    def init_widgets(self):
        """Setting up widgets and layout inside the extraction window."""
        self.window_frame = tk.LabelFrame(self.window, text="Extracting Mode")
        self.window_frame.pack(fill="both", expand=True, padx=15, pady=15)
        self.parameter_frame_widgets()
        self.input_files_frame()
        self.execute_btn = tk.Button(self.window_frame, text="Execute", command=self.execute_extraction)
        self.execute_btn.pack(padx=10, pady=10)

    def parameter_frame_widgets(self):
        """Creating and placing widgets for entering extraction parameters."""
        self.parameters_frame = tk.LabelFrame(self.window_frame)
        self.parameters_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Labels and entries for each parameter with default values pre-inserted
        tk.Label(self.parameters_frame, text="Parameters", font=("Helvetica", 10)).grid(row=0, column=0, columnspan=2,
                                                                                        pady=10)
        tk.Label(self.parameters_frame, text="Key: ").grid(row=1, column=0, sticky="e")
        self.key_entry = tk.Entry(self.parameters_frame)
        self.key_entry.grid(row=1, column=1, sticky="w", pady=5)
        self.key_entry.insert(0, "12345")

        tk.Label(self.parameters_frame, text="Block Size (Bs): ").grid(row=2, column=0, sticky="e")
        self.bs_entry = tk.Entry(self.parameters_frame)
        self.bs_entry.grid(row=2, column=1, sticky="w", pady=5)
        self.bs_entry.insert(0, "256")

        tk.Label(self.parameters_frame, text="Multiplier (Mul): ").grid(row=3, column=0, sticky="e")
        self.mul_entry = tk.Entry(self.parameters_frame)
        self.mul_entry.grid(row=3, column=1, sticky="w", pady=5)
        self.mul_entry.insert(0, "1.2")

        tk.Label(self.parameters_frame, text="Length of embedded data: ").grid(row=4, column=0, sticky="e")
        self.len_embedded_data_entry = tk.Entry(self.parameters_frame)
        self.len_embedded_data_entry.grid(row=4, column=1, sticky="w", pady=5)
        self.len_embedded_data_entry.insert(0, "")

    def input_files_frame(self):
        """Setting up frame and buttons for file input selection."""
        self.file_frame = tk.LabelFrame(self.window_frame)
        self.file_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame for selecting the stego image file
        tk.Label(self.file_frame, text="File inputs", font=("Helvetica", 10)).pack(pady=10)
        image_frame = tk.Frame(self.file_frame)
        image_frame.pack(fill="x", pady=5)
        tk.Label(image_frame, text="Stego image:").pack(side="left")
        tk.Button(image_frame, text="Select File", command=self.select_image_file).pack(side="left", padx=10)
        self.image_file_label = tk.Label(image_frame, text="No file selected")
        self.image_file_label.pack(side="left")

        # Similar setup for selecting the BestSeeds file
        message_frame = tk.Frame(self.file_frame)
        message_frame.pack(fill="x", pady=5)
        tk.Label(message_frame, text="BestSeeds:").pack(side="left")
        tk.Button(message_frame, text="Select File", command=self.select_bestSeeds_file).pack(side="left", padx=10)
        self.bestSeeds_file_label = tk.Label(message_frame, text="No file selected")
        self.bestSeeds_file_label.pack(side="left")

    def select_image_file(self):
        """Open a file dialog to select an image file and update the path."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.tiff;*.tif")])
        if file_path:
            filename = os.path.basename(file_path)
            self.image_file_label.config(text=file_path)  # display full path in the label for clarity
            self.image_path = file_path  # store the full path

    def select_bestSeeds_file(self):
        """Open a file dialog to select best_seeds file and update the path."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.txt;")])
        if file_path:
            filename = os.path.basename(file_path)
            self.bestSeeds_file_label.config(text=file_path)
            self.bestSeeds_path = file_path

    def show_progress_window(self, total_iterations):
        """Setting up progress window."""
        self.progress_window = tk.Toplevel(self.window)
        self.progress_window.title("Embedding Progress")
        self.progress_window.geometry("400x100")  # Adjust size as needed
        self.progress_window.resizable(False, False)

        # Creating a progress bar.
        self.progress = ttk.Progressbar(self.progress_window, orient="horizontal", length=300, mode="determinate",maximum=total_iterations)
        self.progress.pack(pady=20, padx=20)

        # Starting values of progress bar.
        self.progress["value"] = 0


    def execute_extraction(self):
        """Validate parameters and start the embedding process in a new thread."""
        if not self.validate_parameters_extract(self):
            return

        # Preparing algorithm for extraction
        self.prepare_extraction()

        # Creating separate thread for extraction, for displaying progress bar.
        threading.Thread(target=self.run_extracction, daemon=True).start()

    def prepare_extraction(self):
        """Prepare data and settings before starting the extraction process."""
        key = int(self.key_entry.get())
        bs = int(self.bs_entry.get())
        mul = float(self.mul_entry.get())
        len_data = int(self.len_embedded_data_entry.get())

        # Reading stego image.
        stego_image = tifffile.imread(self.image_path)

        # Read best_seeds needed for extraction.
        bestSeeds = read_seeds_from_file(self.bestSeeds_path)

        data_len = len_data * 8

        total_iterations = (stego_image.shape[1] / bs) + 1

        # Showing progress bar.
        self.show_progress_window(total_iterations)

        # Preparing data for method run_extraction that runs on separate thread.
        self.extracting_params = (key, bs, mul, stego_image, bestSeeds, data_len)

    def run_extracction(self):
        """Run the extraction algorithm in a background thread and handle progress."""
        key, bs, mul, stego_image, bestSeeds, data_len = self.extracting_params

        try:
            wcblgExtraction = WCBLGExtraction(stego_image, key, bs, mul, bestSeeds, data_len, self.eng, progress_callback=self.update_progress)
            wcblgExtraction.prepare_algorithm()
            hidden_message = wcblgExtraction.extract_data()
            self.window.after(0, self.finalize_extraction, hidden_message)
        except Exception as e:
            print(f"An error occurred during embedding: {e}")
            self.window.after(0, self.progress_window.destroy)

    def update_progress(self, current_iteration):
        # Using after to safely update the progress bar from the main thread
        self.window.after(0, lambda: self.set_progress(current_iteration))

    def set_progress(self, value):
        # Directly setting the progress bar's value
        self.progress["value"] = value
        self.progress_window.update_idletasks()

    def finalize_extraction(self, hidden_message):
        '''  Finalizes the extraction process by saving the extracted hidden message to a file
        and cleaning up the UI elements like the progress window. '''
        filename = os.path.basename(self.image_path)
        filename_without_ext = os.path.splitext(filename)[0]
        hidden_message_dir = "hidden_message"
        os.makedirs(hidden_message_dir, exist_ok=True)
        hidden_message_path = os.path.join(hidden_message_dir, filename_without_ext + "_message.txt")
        save_hidden_message(hidden_message, hidden_message_path)
        self.progress_window.destroy()

    def is_valid_integer(slef, entry, min_value=None):
        """ Validate if the entry is a valid integer and optionally non-negative. """
        try:
            value = int(entry)
            if min_value is not None and value < min_value:
                return False
            return True
        except ValueError:
            return False

    def is_valid_float(self, entry, min_value=None):
        """ Validate if the entry is a valid float and optionally non-negative. """
        try:
            value = float(entry)
            if min_value is not None and value < min_value:
                return False
            return True
        except ValueError:
            return False

    def is_valid_file_path(self, file_path, extensions=None):
        """ Check if the file path exists and optionally if it matches given extensions. """
        if not os.path.isfile(file_path):
            return False
        if extensions and not any(file_path.endswith(ext) for ext in extensions):
            return False
        return True

    def validate_parameters_extract(self, window):
        """ Validate all parameters from the entry fields for extraction mode. """
        errors = []
        if not self.is_valid_integer(window.key_entry.get(), min_value=0):
            errors.append("Key must be a non-negative integer.")
        if not self.is_valid_integer(window.bs_entry.get(), min_value=1):
            errors.append("Block Size must be a positive integer greater than 0.")
        if not self.is_valid_float(window.mul_entry.get(), min_value=0):
            errors.append("Multiplier must be a non-negative number.")
        if not self.is_valid_integer(window.len_embedded_data_entry.get(), min_value=1):
            errors.append("Length of embedded data must be a positive integer.")
        if not self.is_valid_file_path(window.image_path, [".tiff", ".tif"]):
            errors.append("Selected stego image file is invalid or unsupported.")
        if not self.is_valid_file_path(window.bestSeeds_path, [".txt",]):
            errors.append("Selected BestSeeds file is invalid or unsupported.")

        if errors:
            tk.messagebox.showerror("Parameter Error", "\n".join(errors))
            return False
        return True
