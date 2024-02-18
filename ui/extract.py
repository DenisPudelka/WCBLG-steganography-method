import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from stego.Utils import *
from stego.WCBLGExtraction_version_2 import WCBLGExtraction
import tifffile
import threading


class ExtractMode:
    def __init__(self, eng):
        self.eng = eng
        self.image_path = ''
        self.bestSeeds_path = ''
        self.window = tk.Toplevel()
        self.window.geometry("500x700")
        self.window.resizable(False, False)
        self.window.title("Extract Mode")
        self.init_widgets()

    def init_widgets(self):
        self.window_frame = tk.LabelFrame(self.window, text="Extracting Mode")
        self.window_frame.pack(fill="both", expand=True, padx=15, pady=15)
        self.parameter_frame_widgets()
        self.transformation_frame_widgets()
        self.input_files_frame()
        self.execute_btn = tk.Button(self.window_frame, text="Execute", command=self.execute_extraction)
        self.execute_btn.pack(padx=10, pady=10)

    def parameter_frame_widgets(self):
        self.parameters_frame = tk.LabelFrame(self.window_frame)
        self.parameters_frame.pack(fill="both", expand=True, padx=10, pady=10)

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

        tk.Label(image_frame, text="Stego image:").pack(side="left")
        tk.Button(image_frame, text="Select File", command=self.select_image_file).pack(side="left", padx=10)
        self.image_file_label = tk.Label(image_frame, text="No file selected")
        self.image_file_label.pack(side="left")

        message_frame = tk.Frame(self.file_frame)
        message_frame.pack(fill="x", pady=5)

        tk.Label(message_frame, text="BestSeeds:").pack(side="left")
        tk.Button(message_frame, text="Select File", command=self.select_bestSeeds_file).pack(side="left", padx=10)
        self.bestSeeds_file_label = tk.Label(message_frame, text="No file selected")
        self.bestSeeds_file_label.pack(side="left")

    def select_image_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff;*.tif")])
        if file_path:
            filename = os.path.basename(file_path)
            self.image_file_label.config(text=file_path)
            self.image_path = filename

    def select_bestSeeds_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.txt;*.csv")])
        if file_path:
            filename = os.path.basename(file_path)
            self.bestSeeds_file_label.config(text=file_path)
            self.bestSeeds_path = filename

    def show_progress_window(self, total_iterations):
        self.progress_window = tk.Toplevel(self.window)
        self.progress_window.title("Embedding Progress")
        self.progress_window.geometry("400x100")  # Adjust size as needed
        self.progress_window.resizable(False, False)

        # Creating a progress bar
        self.progress = ttk.Progressbar(self.progress_window, orient="horizontal", length=300, mode="determinate",maximum=total_iterations)
        self.progress.pack(pady=20, padx=20)

        # Starting values of progress bar
        self.progress["value"] = 0


    def execute_extraction(self):
        self.prepare_extraction()

        # Creating separate thread for extraction, so I can on separate thread display progress bar
        threading.Thread(target=self.run_extracction, daemon=True).start()

    def prepare_extraction(self):
        key = int(self.key_entry.get())
        bs = int(self.bs_entry.get())
        mul = float(self.mul_entry.get())
        len_data = int(self.len_embedded_data_entry.get())

        use_iwt = True

        stego_image = tifffile.imread("stego_image/" + self.image_path)

        # read best seeds
        bestSeeds = read_seeds_from_file("seeds_keys/" + self.bestSeeds_path)

        data_len = len_data * 8

        total_iterations = (stego_image.shape[1] / bs) + 1

        self.show_progress_window(total_iterations)

        self.extracting_params = (key, bs, mul, use_iwt, stego_image, bestSeeds, data_len)

    def run_extracction(self):
        # This method runs in a separate thread and contains the embedding logic
        key, bs, mul, use_iwt, stego_image, bestSeeds, data_len = self.extracting_params

        try:
            wcblgExtraction = WCBLGExtraction(stego_image, key, bs, mul, bestSeeds, data_len, self.eng, use_iwt, progress_callback=self.update_progress)
            wcblgExtraction.prepare_algorithm()
            hidden_message = wcblgExtraction.extract_data()

            self.window.after(0, self.finalize_embedding, hidden_message)
        except Exception as e:
            print(f"An error occurred during embedding: {e}")
            # Ensure the progress window is closed even if there's an error
            self.window.after(0, self.progress_window.destroy)

    def update_progress(self, current_iteration):
        # using after to safely update the progress bar from the main thread
        self.window.after(0, lambda: self.set_progress(current_iteration))

    def set_progress(self, value):
        # directly setting the progress bar's value
        self.progress["value"] = value
        self.progress_window.update_idletasks()  # ensuring the GUI is updated

    def finalize_embedding(self, hidden_message):
        print(hidden_message)
        save_hidden_message(hidden_message, "hidden_message/")
        self.progress_window.destroy()
