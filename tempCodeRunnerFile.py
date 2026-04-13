import tkinter as tk
from tkinter import scrolledtext
import subprocess
import os

def run_code():
    input_code = text_editor.get("1.0", tk.END).strip()
    
    # Save code to temp file
    with open("temp_input.txt", "w") as f:
        f.write(input_code)
    
    try:
        # Run the compiled interpreter.exe
        process = subprocess.Popen(
            'interpreter.exe < temp_input.txt', 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )
        stdout, stderr = process.communicate()
        
        output_console.config(state=tk.NORMAL)
        output_console.delete("1.0", tk.END)
        
        # Color coding for errors vs output
        output_console.tag_configure("red", foreground="#ff4d4d")
        output_console.tag_configure("green", foreground="#00ff00")

        if stderr:
            output_console.insert(tk.END, stderr, "red")
        if stdout:
            output_console.insert(tk.END, stdout, "green")
            
        output_console.config(state=tk.DISABLED)
        
    except Exception as e:
        output_console.config(state=tk.NORMAL)
        output_console.insert(tk.END, f"SYSTEM ERROR: {str(e)}", "red")
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
output_console.config(state=tk.DISABLED)
output_console.pack(fill=tk.BOTH, padx=20, pady=10)

root.mainloop()