import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog, messagebox
import subprocess
import os
import sys

def run_code():
    input_code = text_editor.get("1.0", tk.END)
    if not input_code.strip():
        update_output("No code to run.\n", "red")
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
        status_var.set("Code executed successfully")

    except Exception as e:
        update_output(f"SYSTEM ERROR: {str(e)}\n", "red")
        status_var.set("Execution failed")

def update_output(text, tag):
    output_console.config(state=tk.NORMAL)
    output_console.insert(tk.END, text, tag)
    output_console.config(state=tk.DISABLED)

def new_file():
    text_editor.delete("1.0", tk.END)
    text_editor.insert(tk.END, "start {\n    eshow(\"Welcome to my Compiler\");\n} end")
    status_var.set("New file created")

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as f:
            text_editor.delete("1.0", tk.END)
            text_editor.insert(tk.END, f.read())
        status_var.set(f"Opened {file_path}")

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as f:
            f.write(text_editor.get("1.0", tk.END))
        status_var.set(f"Saved {file_path}")

def highlight_syntax(event=None):
    text_editor.tag_remove("keyword", "1.0", tk.END)
    text_editor.tag_remove("string", "1.0", tk.END)
    text_editor.tag_remove("comment", "1.0", tk.END)
    
    content = text_editor.get("1.0", tk.END)
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        # Keywords
        keywords = ["start", "end", "num", "eshow"]
        for kw in keywords:
            start = f"{i}.0"
            while True:
                pos = text_editor.search(kw, start, stopindex=f"{i}.end")
                if not pos:
                    break
                end = f"{pos}+{len(kw)}c"
                text_editor.tag_add("keyword", pos, end)
                start = end
        
        # Strings
        import re
        for match in re.finditer(r'\"[^\"]*\"', line):
            start_pos = f"{i}.{match.start()}"
            end_pos = f"{i}.{match.end()}"
            text_editor.tag_add("string", start_pos, end_pos)

# UI Setup
root = tk.Tk()
root.title("GOGA C CMPILER")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")

# Style
style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", background="#2d2d2d", foreground="#b5cea8", font=("Consolas", 10, "bold"))
style.configure("TLabel", background="#1e1e1e", foreground="#569cd6")

# Menu
menubar = tk.Menu(root, bg="#2d2d2d", fg="#d4d4d4")
filemenu = tk.Menu(menubar, tearoff=0, bg="#2d2d2d", fg="#d4d4d4")
filemenu.add_command(label="New", command=new_file, accelerator="Ctrl+N")
filemenu.add_command(label="Open", command=open_file, accelerator="Ctrl+O")
filemenu.add_command(label="Save", command=save_file, accelerator="Ctrl+S")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

editmenu = tk.Menu(menubar, tearoff=0, bg="#2d2d2d", fg="#d4d4d4")
editmenu.add_command(label="Cut", command=lambda: text_editor.event_generate("<<Cut>>"))
editmenu.add_command(label="Copy", command=lambda: text_editor.event_generate("<<Copy>>"))
editmenu.add_command(label="Paste", command=lambda: text_editor.event_generate("<<Paste>>"))
menubar.add_cascade(label="Edit", menu=editmenu)

runmenu = tk.Menu(menubar, tearoff=0, bg="#2d2d2d", fg="#d4d4d4")
runmenu.add_command(label="Run Code", command=run_code, accelerator="F5")
menubar.add_cascade(label="Run", menu=runmenu)

root.config(menu=menubar)

# Toolbar
toolbar = tk.Frame(root, bg="#2d2d2d")
toolbar.pack(side=tk.TOP, fill=tk.X)

ttk.Button(toolbar, text="New", command=new_file).pack(side=tk.LEFT, padx=2, pady=2)
ttk.Button(toolbar, text="Open", command=open_file).pack(side=tk.LEFT, padx=2, pady=2)
ttk.Button(toolbar, text="Save", command=save_file).pack(side=tk.LEFT, padx=2, pady=2)
ttk.Button(toolbar, text="Run", command=run_code).pack(side=tk.LEFT, padx=2, pady=2)

# Main frame
main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Title
ttk.Label(main_frame, text="GOGA C CMPILER", font=("Consolas", 16, "bold")).pack(pady=10)

# Paned window for editor and output
paned = tk.PanedWindow(main_frame, orient=tk.VERTICAL, bg="#1e1e1e")
paned.pack(fill=tk.BOTH, expand=True)

# Editor frame
editor_frame = tk.Frame(paned, bg="#1e1e1e")
paned.add(editor_frame, minsize=300)

ttk.Label(editor_frame, text="Code Editor", font=("Consolas", 12)).pack(anchor=tk.W, padx=5, pady=5)

text_editor = scrolledtext.ScrolledText(editor_frame, height=20, bg="#252526", fg="#d4d4d4", insertbackground="white", font=("Consolas", 12), wrap=tk.WORD)
text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
text_editor.insert(tk.END, "start {\n    eshow(\"Welcome to my Compiler\");\n} end")

# Syntax highlighting tags
text_editor.tag_configure("keyword", foreground="#569cd6", font=("Consolas", 12, "bold"))
text_editor.tag_configure("string", foreground="#ce9178")
text_editor.tag_configure("comment", foreground="#6a9955")

text_editor.bind("<KeyRelease>", highlight_syntax)
highlight_syntax()  # Initial highlight

# Output frame
output_frame = tk.Frame(paned, bg="#1e1e1e")
paned.add(output_frame, minsize=200)

ttk.Label(output_frame, text="Output Console", font=("Consolas", 12)).pack(anchor=tk.W, padx=5, pady=5)

output_console = scrolledtext.ScrolledText(output_frame, height=10, bg="#000000", fg="#d4d4d4", font=("Consolas", 11), wrap=tk.WORD)
output_console.tag_configure("red", foreground="#ff4d4d")
output_console.tag_configure("green", foreground="#00ff00")
output_console.config(state=tk.DISABLED)
output_console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Status bar
status_var = tk.StringVar()
status_var.set("Ready")
status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Bindings
root.bind("<Control-n>", lambda e: new_file())
root.bind("<Control-o>", lambda e: open_file())
root.bind("<Control-s>", lambda e: save_file())
root.bind("<F5>", lambda e: run_code())

root.mainloop()