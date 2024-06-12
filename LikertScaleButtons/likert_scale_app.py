import serial
import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime

class LikertScaleApp:
    def __init__(self, master):
        self.master = master
        master.title("Likert Scale Experiment Interface")

        self.frame_top = tk.Frame(master)
        self.frame_top.pack(pady=10)

        self.frame_mid = tk.Frame(master)
        self.frame_mid.pack(pady=10)

        self.frame_bottom = tk.Frame(master)
        self.frame_bottom.pack(pady=10)

        # Widgets for COM port selection
        self.com_label = tk.Label(self.frame_top, text="COM Port:", font=("Arial", 14))
        self.com_label.pack(side=tk.LEFT)

        self.com_entry = tk.Entry(self.frame_top, font=("Arial", 14), width=10)
        self.com_entry.pack(side=tk.LEFT)

        # Widgets for metadata
        self.study_label = tk.Label(self.frame_top, text="Study Name:", font=("Arial", 14))
        self.study_label.pack(side=tk.LEFT)

        self.study_entry = tk.Entry(self.frame_top, font=("Arial", 14), width=20)
        self.study_entry.pack(side=tk.LEFT)

        # Widgets for file naming
        self.filename_label = tk.Label(self.frame_top, text="Enter Filename:", font=("Arial", 14))
        self.filename_label.pack(side=tk.LEFT)

        self.filename_entry = tk.Entry(self.frame_top, font=("Arial", 14), width=20)
        self.filename_entry.pack(side=tk.LEFT)

        # Buttons for start and stop
        self.start_button = tk.Button(self.frame_mid, text="Start", font=("Arial", 14), command=self.start_experiment)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(self.frame_mid, text="Stop", font=("Arial", 14), command=self.stop_experiment)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Response buttons
        self.buttons = [tk.Button(self.frame_bottom, text=str(i+1), font=("Arial", 14), width=10,
                                  command=lambda i=i: self.log_response(i+1)) for i in range(5)]
        for button in self.buttons:
            button.pack(side=tk.LEFT, padx=10)

        self.response_label = tk.Label(master, text="", font=("Arial", 14))
        self.response_label.pack(pady=10)

        self.ser = None
        self.is_collecting = False
        self.file = None
        self.start_time = None

    def start_experiment(self):
        com_port = self.com_entry.get()
        if not com_port:
            messagebox.showerror("Error", "Please enter the COM port.")
            return

        try:
            self.ser = serial.Serial(com_port, 9600, timeout=1)
        except serial.SerialException:
            messagebox.showerror("Error", "Could not open COM port. Please check the connection and try again.")
            return

        filename = self.filename_entry.get()
        study_name = self.study_entry.get()
        if filename and study_name:
            self.file = open(filename + ".csv", "a")
            self.file.write(f"Study: {study_name}, Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.file.write("Timestamp,Participant,Response\n")
            self.is_collecting = True
            self.start_time = datetime.datetime.now()
            self.filename_entry.config(state='disabled')
            self.study_entry.config(state='disabled')
            self.com_entry.config(state='disabled')
            self.start_button.config(state='disabled')
            self.response_label.config(text="Experiment started. Collecting data...")
        else:
            messagebox.showerror("Error", "Please enter all fields to start.")

    def stop_experiment(self):
        if self.is_collecting:
            self.is_collecting = False
            self.file.write(f"End Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.file.close()
            self.ser.close()
            self.response_label.config(text="Experiment stopped. Data collection is paused.")
            self.filename_entry.config(state='normal')
            self.study_entry.config(state='normal')
            self.com_entry.config(state='normal')
            self.start_button.config(state='normal')
            self.prompt_for_next_action()

    def prompt_for_next_action(self):
        answer = messagebox.askyesno("Continue", "Do you want to add another participant to the same study?")
        if answer:
            self.start_experiment()
        else:
            self.filename_entry.config(state='normal')
            self.study_entry.config(state='normal')
            self.start_button.config(state='normal')

    def log_response(self, response):
        if self.is_collecting:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.file.write(f"{timestamp},{response}\n")
            self.response_label.config(text=f"Response Recorded: {response} at {timestamp}")

    def read_serial(self):
        if self.is_collecting and self.ser.in_waiting:
            line = self.ser.readline().decode('utf-8').strip()
            if line:
                self.log_response(line)

        self.master.after(100, self.read_serial)  # Check every 100ms

root = tk.Tk()
app = LikertScaleApp(root)
root.after(100, app.read_serial)  # Start reading serial data
root.mainloop()
