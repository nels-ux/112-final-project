import tkinter as tk
from tkinter import scrolledtext
import subprocess
import os
import sys

def run_code():
    input_code = text_editor.get("1.0", tk.END)
    if not input_code.strip():
        output_console.config(state=tk.NORMAL)
        output_console.delete("1.0", tk.END)
        output_console.insert(tk.END, "No code to run.\n", "red")
        output_console.config(state=tk.DISABLED)
        return

    try:
        script_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        exe_path = os.path.join(script_dir, 'interpreter.exe')
        if not os.path.isfile(exe_path):
            raise FileNotFoundError(f"interpreter.exe not found at {exe_path}")

        process = subprocess.Popen(
            [exe_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=input_code, timeout=10)

        output_console.config(state=tk.NORMAL)
        output_console.delete("1.0", tk.END)

        if stderr:
            output_console.insert(tk.END, stderr, "red")
        if stdout:
            output_console.insert(tk.END, stdout, "green")
        if not stdout and not stderr:
            output_console.insert(tk.END, "[No output produced]\n", "green")

        output_console.config(state=tk.DISABLED)

    except Exception as e:
        output_console.config(state=tk.NORMAL)
        output_console.delete("1.0", tk.END)
        output_console.insert(tk.END, f"SYSTEM ERROR: {str(e)}\n", "red")
        output_console.config(state=tk.DISABLED)

# UI Setup
root = tk.Tk()
root.title("GOGA C")
root.geometry("800x650")
root.configure(bg="#1e1e1e")

# Title
tk.Label(root, text="KALOY E MI SIR", bg="#1e1e1e", fg="#569cd6", font=("Consolas", 14, "bold")).pack(pady=10)

# Editor
text_editor = scrolledtext.ScrolledText(root, height=18, bg="#252526", fg="#d4d4d4", insertbackground="white", font=("Consolas", 12))
text_editor.pack(fill=tk.BOTH, padx=20, pady=5)
text_editor.insert(tk.END, "start {\n    eshow(\"Welcome to my Compiler\");\n} end")

# Run Button
run_btn = tk.Button(root, text="RUN", bg="#2d2d2d", fg="#b5cea8", font=("Consolas", 12, "bold"), command=run_code, borderwidth=1)
run_btn.pack(pady=10)

# Output
output_console = scrolledtext.ScrolledText(root, height=8, bg="#000000", font=("Consolas", 11))
output_console.tag_configure("red", foreground="#ff4d4d")
output_console.tag_configure("green", foreground="#00ff00")
output_console.config(state=tk.DISABLED)
output_console.pack(fill=tk.BOTH, padx=20, pady=10)

root.mainloop()