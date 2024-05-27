import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from stego.Utils import *   # Utility functions
from stego.WCBLGAlgorithm_version_2 import WCBLGAlgorithm   # Embedding algorithm
import tifffile # For reading TIFF files
import threading


class EmbedMode:
    def __init__(self, eng):
        """Initialize the embedding GUI with a reference to an engine and default values."""
        self.eng = eng  # Engine used for Matlab
        self.image_path = ''
        self.message_path = ''
        self.window = tk.Toplevel()
        self.embedding_params = None
        self.window.geometry("500x700")
        self.window.resizable(True, False)
        self.window.title("Embed Mode")
        self.init_widgets() # Initializing the widgets inside window

    def init_widgets(self):
        """Setup widgets and layout inside the embedding window."""
        self.window_frame = tk.LabelFrame(self.window, text="Embedding Mode")
        self.window_frame.pack(fill="both", expand=True, padx=15, pady=15)
        self.parameter_frame_widgets()
        self.input_files_frame()
        self.execute_btn = tk.Button(self.window_frame, text="Execute", command=self.execute_embedding)
        self.execute_btn.pack(padx=10, pady=10)

    def parameter_frame_widgets(self):
        """Creating and placing widgets for entering embedding parameters."""
        self.parameters_frame = tk.LabelFrame(self.window_frame)
        self.parameters_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Labels and entries for each parameter with default values pre-inserted
        tk.Label(self.parameters_frame, text="Parameters", font=("Helvetica", 10)).grid(row=0, column=1, columnspan=2,pady=10)
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

        tk.Label(self.parameters_frame, text="Population Size (Npop): ").grid(row=4, column=0, sticky="e")
        self.pop_size_entry = tk.Entry(self.parameters_frame)
        self.pop_size_entry.grid(row=4, column=1, sticky="w", pady=5)
        self.pop_size_entry.insert(0, "50")

        tk.Label(self.parameters_frame, text="Crossover (Pc): ").grid(row=5, column=0, sticky="e")
        self.crossover_entry = tk.Entry(self.parameters_frame)
        self.crossover_entry.grid(row=5, column=1, sticky="w", pady=5)
        self.crossover_entry.insert(0, "0.7")

        tk.Label(self.parameters_frame, text="Mutation (Pm): ").grid(row=6, column=0, sticky="e")
        self.mutation_entry = tk.Entry(self.parameters_frame)
        self.mutation_entry.grid(row=6, column=1, sticky="w", pady=5)
        self.mutation_entry.insert(0, "0.2")

        tk.Label(self.parameters_frame, text="Epoch: ").grid(row=7, column=0, sticky="e")
        self.epoch_entry = tk.Entry(self.parameters_frame)
        self.epoch_entry.grid(row=7, column=1, sticky="ew", pady=5)
        self.epoch_entry.insert(0, "20")

    def input_files_frame(self):
        """Setting up frame and buttons for file input selection."""
        self.file_frame = tk.LabelFrame(self.window_frame)
        self.file_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame for selecting the cover image file
        tk.Label(self.file_frame, text="File inputs", font=("Helvetica", 10)).pack(pady=10)
        image_frame = tk.Frame(self.file_frame)
        image_frame.pack(fill="x", pady=5)
        tk.Label(image_frame, text="Cover image:").pack(side="left")
        tk.Button(image_frame, text="Select File", command=self.select_image_file).pack(side="left", padx=10)
        self.image_file_label = tk.Label(image_frame, text="No file selected")
        self.image_file_label.pack(side="left")

        # Frame for selecting the message that will be embedded
        message_frame = tk.Frame(self.file_frame)
        message_frame.pack(fill="x", pady=5)
        tk.Label(message_frame, text="Message:").pack(side="left")
        tk.Button(message_frame, text="Select File", command=self.select_message_file).pack(side="left", padx=10)
        self.message_file_label = tk.Label(message_frame, text="No file selected")
        self.message_file_label.pack(side="left")

    def select_image_file(self):
        """Open a file dialog to select an image file and update the path."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.tiff;*.tif")])
        if file_path:
            filename = os.path.basename(file_path)
            self.image_file_label.config(text=file_path)
            self.image_path = file_path

    def select_message_file(self):
        """Open a file dialog to select a message file and update the path."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.txt;")])
        if file_path:
            filename = os.path.basename(file_path)
            self.message_file_label.config(text=file_path)
            self.message_path = file_path

    def show_progress_window(self, total_iterations):
        """Setting up progress window."""
        self.progress_window = tk.Toplevel(self.window)
        self.progress_window.title("Embedding Progress")
        self.progress_window.geometry("400x100")  # Adjust size as needed
        self.progress_window.resizable(False, False)

        # Creating a progress bar
        self.progress = ttk.Progressbar(self.progress_window, orient="horizontal", length=300, mode="determinate",maximum=total_iterations)
        self.progress.pack(pady=20, padx=20)

        # Starting values of progress bar
        self.progress["value"] = 0

    def execute_embedding(self):
        """Validate parameters and start the embedding process in a new thread."""
        if not self.validate_parameters(self):
            return

        # Preparing algorithm for embedding
        self.prepare_embedding()

        # Creating separate thread for embedding, for displaying progress bar
        threading.Thread(target=self.run_embedding, daemon=True).start()

    def prepare_embedding(self):
        """Prepare data and settings before starting the embedding process."""
        key = int(self.key_entry.get())
        bs = int(self.bs_entry.get())
        mul = float(self.mul_entry.get())
        pop_size = int(self.pop_size_entry.get())
        pc = float(self.crossover_entry.get())
        pm = float(self.mutation_entry.get())
        epoch = int(self.epoch_entry.get())

        # Reading image where message will be embedded.
        image_original = tifffile.imread(self.image_path)

        # Convert image to grayscale if not.
        size = len(image_original.shape)
        if size == 3:
            image_original = color_to_gray_matlab(image_original, self.eng)

        # Prepare image, making sure cover image stays in 8-bit color depth.
        image_original = self.prepare_image(image_original)

        # Convert image to different datatype.
        cover_image = convert_image_to_datatype_matlab(image_original, "uint8", self.eng)

        # Reading message that will be embedded into cover image.
        data = read_message(self.message_path)

        total_iterations = (image_original.shape[1] / bs) + 1

        # Showing progress bar.
        self.show_progress_window(total_iterations)

        # Preparing data for method run_embedding that runs on separate thread.
        self.embedding_params = (key, bs, mul, pop_size, pc, pm, epoch, cover_image, data)

    def run_embedding(self):
        """Run the embedding algorithm in a background thread and handle progress."""
        key, bs, mul, pop_size, pc, pm, epoch, cover_image, data = self.embedding_params

        try:
            wcblgEmbedding = WCBLGAlgorithm(cover_image, data, key, bs, mul, pop_size, pc, pm, epoch, self.eng, progress_callback=self.update_progress)
            if not wcblgEmbedding.prepare_algorithm():
                print("embedding went wrong")
            bestSeeds, stego_image = wcblgEmbedding.wcblg()
            self.window.after(0, self.finalize_embedding, bestSeeds, stego_image, cover_image)
        except Exception as e:
            print(f"An error occurred during embedding: {e}")
            self.window.after(0, self.progress_window.destroy)

    def update_progress(self, current_iteration):
        # Using after to safely update the progress bar from the main thread.
        self.window.after(0, lambda: self.set_progress(current_iteration))

    def set_progress(self, value):
        # Directly setting the progress bar's value.
        self.progress["value"] = value
        self.progress_window.update_idletasks()

    def finalize_embedding(self, bestSeeds, stego_image, cover_image):
        write_seeds_to_file(bestSeeds, "best_seeds.txt")
        # Extract the filename from the full path
        filename = os.path.basename(self.image_path)

        # Define the directories relative to the current script's location in 'ui' directory.
        # Define the directories directly since the script is run from the root directory.
        cover_dir = "cover_image"
        stego_dir = "stego_image"

        # Ensure directories exist.
        os.makedirs(cover_dir, exist_ok=True)
        os.makedirs(stego_dir, exist_ok=True)

        # Paths for saving images.
        cover_image_path = os.path.join(cover_dir, filename)
        stego_image_path = os.path.join(stego_dir, filename)

        print(f"Saving cover image, type: {type(cover_image)}, dtype: {cover_image.dtype}")
        print("Cover image path:", cover_image_path)
        save_image(cover_image, cover_image_path)

        print(f"Saving stego image, type: {type(stego_image)}, dtype: {stego_image.dtype}")
        print("Stego image path:", stego_image_path)
        save_image(stego_image, stego_image_path)

        self.progress_window.destroy()

    def prepare_image(self, image):
        row, col = image.shape
        for x in range(row):
            for y in range(col):
                if image[x, y] == 0:
                    image[x, y] += 1
                elif image[x, y] == 255:
                    image[x, y] -= 1
        return image

    def is_valid_integer(self, entry, min_value=None, max_value=None):
        """ Validate if the entry is a valid integer and optionally within a specified range. """
        try:
            value = int(entry)
            if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                return False
            return True
        except ValueError:
            return False

    def is_valid_float(self, entry, min_value=None, max_value=None):
        """ Validate if the entry is a valid float and optionally within a specified range. """
        try:
            value = float(entry)
            if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                return False
            return True
        except ValueError:
            return False

    def is_valid_file_path(self, file_path, extensions=None):
        """ Check if the file path exists and optionally if it matches the given extensions. """
        if not os.path.isfile(file_path):
            return False
        if extensions and not any(file_path.endswith(ext) for ext in extensions):
            return False
        return True

    def validate_parameters(self, window):
        """ Validate all parameters from the entry fields. Show errors in a message box if invalid. """
        errors = []
        if not self.is_valid_integer(window.key_entry.get(), min_value=0):
            errors.append("Key must be a positive integer.")
        if not self.is_valid_integer(window.bs_entry.get(), min_value=1):
            errors.append("Block Size must be a positive integer greater than 0.")
        if not self.is_valid_float(window.mul_entry.get(), min_value=0):
            errors.append("Multiplier must be a positive number.")
        if not self.is_valid_integer(window.pop_size_entry.get(), min_value=1, max_value=100):
            errors.append("Population Size must be a positive integer greater between 1 and 100.")
        if not self.is_valid_float(window.crossover_entry.get(), min_value=0, max_value=1):
            errors.append("Crossover probability must be between 0 and 1.")
        if not self.is_valid_float(window.mutation_entry.get(), min_value=0, max_value=1):
            errors.append("Mutation probability must be between 0 and 1.")
        if not self.is_valid_integer(window.epoch_entry.get(), min_value=1):
            errors.append("Epoch must be a positive integer greater than 0.")
        if not self.is_valid_file_path(window.image_path, [".tiff", ".tif"]):
            errors.append("Selected image file is invalid or unsupported.")
        if not self.is_valid_file_path(window.message_path, [".txt"]):
            errors.append("Selected message file is invalid or unsupported.")

        if errors:
            tk.messagebox.showerror("Parameter Error", "\n".join(errors))
            return False
        return True