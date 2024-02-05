import tkinter as tk


class AlgorithmParameterUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="lightgray", bd=2, relief="groove")
        self.initWidgets()

    def initWidgets(self):
        tk.Label(self, text="WCBLG Parameters", font=("Heôventica", 16,), bg="lightgray").grid(row=0, column=0, columnspan=2)

        self.createEntry("Key:", "e.g., 12345", 1)
        self.createEntry("Block Size (Bs):", "e.g., 256", 2)
        self.createEntry("Multiplier (Mul):", "e.g., 1.2", 3)
        self.createEntry("Population Size (Npop):", "e.g., 20", 4)
        self.createEntry("Crossover (Pc):", "e.g., 0.7", 5)
        self.createEntry("Mutation (Pm):", "e.g., 0.2", 6)
        self.createEntry("Epoch:", "e.g., 20", 7)

        method = tk.StringVar(value="DWT")
        tk.Radiobutton(self, text="DWT", variable=method, value="DWT", bg="lightgray").grid(row=8, column=0)
        tk.Radiobutton(self, text="IWT", variable=method, value="IWT", bg="lightgray").grid(row=8, column=1)


    def createEntry(self, label, placeholder, row):
        tk.Label(self, text=label, bg="lightgray").grid(row=row, column=0)
        entry = tk.Entry(self)
        entry.grid(row=row, column=1)
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda args: entry.delete(0, 'end'))
        entry.bind("<FocusOut>", lambda args: entry.insert(0, placeholder) if not entry.get() else None)
