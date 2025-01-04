import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess


class AdminUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UCU Attendance System")
        self.root.geometry("200x300")  # Set the window size to 400x300 pixels

        # add label
        self.label = ttk.Label(self.root, text="UCU Attendance System")
        self.label.pack(pady=20)

        self.generate_faces_button = ttk.Button(
            self.root, text="Generate Faces", command=self.generate_faces
        )
        self.generate_faces_button.pack(pady=20)

        self.open_face_recog = ttk.Button(
            self.root, text="Open Face Recognition", command=self.open_face_recog
        )
        self.open_face_recog.pack(pady=20)

    def generate_faces(self):
        self.disable_buttons()
        self.run_command("python EncodeGenerator.py")
        self.enable_buttons()

    def open_face_recog(self):
        self.disable_buttons()
        self.run_command("python main.py")
        self.enable_buttons()

    def run_command(self, command):
        output_window = tk.Toplevel(self.root)
        output_window.title("Command Output")
        output_window.geometry("600x400")

        text_widget = tk.Text(output_window)
        text_widget.pack(expand=True, fill=tk.BOTH)

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()

        text_widget.insert(tk.END, stdout)
        if stderr:
            text_widget.insert(tk.END, "\nErrors:\n" + stderr)

        if process.returncode == 0:
            messagebox.showinfo("Success", "Command executed successfully.")
        else:
            messagebox.showerror("Error", "An error occurred during command execution.")

    def disable_buttons(self):
        self.generate_faces_button.config(state=tk.DISABLED)
        self.open_face_recog.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.generate_faces_button.config(state=tk.NORMAL)
        self.open_face_recog.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = AdminUI(root)
    root.mainloop()
