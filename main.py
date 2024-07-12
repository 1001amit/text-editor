import tkinter as tk
from tkinter import filedialog, font, messagebox
import os

RECENT_FILES_PATH = "recent_files.txt"

def load_recent_files():
    if os.path.exists(RECENT_FILES_PATH):
        with open(RECENT_FILES_PATH, "r") as file:
            return file.read().splitlines()
    return []

def save_recent_files():
    with open(RECENT_FILES_PATH, "w") as file:
        for file_path in recent_files:
            file.write(file_path + "\n")

def update_recent_files(file_path):
    if file_path in recent_files:
        recent_files.remove(file_path)
    recent_files.insert(0, file_path)
    if len(recent_files) > 10:
        recent_files.pop()
    save_recent_files()
    update_recent_files_menu()

def update_recent_files_menu():
    recent_files_menu.delete(0, tk.END)
    for file_path in recent_files:
        recent_files_menu.add_command(label=file_path, command=lambda path=file_path: open_recent_file(path))

def open_recent_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, file.read())
        update_recent_files(file_path)
    else:
        messagebox.showerror("Error", f"File not found: {file_path}")

def new_file():
    text_area.delete(1.0, tk.END)
    update_status_bar()

def open_file():
    file_path = filedialog.askopenfilename(defaultextension=".txt", 
                                           filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, file.read())
        update_recent_files(file_path)
        update_status_bar()

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(text_area.get(1.0, tk.END))
        update_recent_files(file_path)

def cut_text():
    text_area.event_generate("<<Cut>>")
    update_status_bar()

def copy_text():
    text_area.event_generate("<<Copy>>")

def paste_text():
    text_area.event_generate("<<Paste>>")
    update_status_bar()

def select_all():
    text_area.tag_add('sel', '1.0', 'end')

def clear_selection():
    text_area.tag_remove('sel', '1.0', 'end')

def undo_action():
    try:
        text_area.edit_undo()
    except tk.TclError:
        pass
    update_status_bar()

def redo_action():
    try:
        text_area.edit_redo()
    except tk.TclError:
        pass
    update_status_bar()

def zoom_in():
    current_font_size = text_font.actual()["size"]
    text_font.config(size=current_font_size + 2)

def zoom_out():
    current_font_size = text_font.actual()["size"]
    text_font.config(size=current_font_size - 2)

def default_zoom():
    text_font.config(size=12)

def toggle_full_screen():
    global is_full_screen
    is_full_screen = not is_full_screen
    root.attributes("-fullscreen", is_full_screen)

def exit_full_screen(event=None):
    global is_full_screen
    is_full_screen = False
    root.attributes("-fullscreen", False)

def find_text():
    find_dialog = tk.Toplevel(root)
    find_dialog.title("Find and Replace")
    find_dialog.transient(root)
    
    tk.Label(find_dialog, text="Find:").grid(row=0, column=0, padx=4, pady=4)
    tk.Label(find_dialog, text="Replace:").grid(row=1, column=0, padx=4, pady=4)
    
    find_entry = tk.Entry(find_dialog, width=30)
    find_entry.grid(row=0, column=1, padx=4, pady=4)
    
    replace_entry = tk.Entry(find_dialog, width=30)
    replace_entry.grid(row=1, column=1, padx=4, pady=4)
    
    def find():
        text_area.tag_remove('highlight', '1.0', tk.END)
        find_text = find_entry.get()
        if find_text:
            idx = '1.0'
            while True:
                idx = text_area.search(find_text, idx, nocase=1, stopindex=tk.END)
                if not idx:
                    break
                lastidx = '%s+%dc' % (idx, len(find_text))
                text_area.tag_add('highlight', idx, lastidx)
                idx = lastidx
            text_area.tag_config('highlight', background='yellow')
    
    def replace():
        find_text = find_entry.get()
        replace_text = replace_entry.get()
        content = text_area.get("1.0", tk.END)
        new_content = content.replace(find_text, replace_text)
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", new_content)
    
    tk.Button(find_dialog, text="Find", command=find).grid(row=2, column=0, padx=4, pady=4)
    tk.Button(find_dialog, text="Replace", command=replace).grid(row=2, column=1, padx=4, pady=4)
    
    find_dialog.mainloop()

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)

def on_change(event):
    text_line_numbers.redraw()
    update_status_bar()

def update_status_bar(event=None):
    row, col = text_area.index(tk.INSERT).split('.')
    line_count = int(text_area.index(tk.END).split('.')[0]) - 1
    char_count = len(text_area.get(1.0, tk.END)) - 1
    word_count = len(text_area.get(1.0, tk.END).split())
    status_text.set(f"Line: {row} | Column: {col} | Lines: {line_count} | Words: {word_count} | Characters: {char_count}")

# Create the main window
root = tk.Tk()
root.title("Simple Text Editor")
root.geometry("800x600")

# Initialize full screen state
is_full_screen = False

# Create a text area
text_font = font.Font(family="Helvetica", size=12)
text_area = tk.Text(root, wrap="word", font=text_font, undo=True)
text_area.pack(expand=1, fill="both", side="right")

# Create line numbers
text_line_numbers = TextLineNumbers(root, width=30)
text_line_numbers.attach(text_area)
text_line_numbers.pack(side="left", fill="y")

# Bind events for line numbers
text_area.bind("<KeyPress>", on_change)
text_area.bind("<ButtonRelease>", on_change)

# Create a status bar frame
status_bar_frame = tk.Frame(root)
status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Create a horizontal scrollbar
x_scroll = tk.Scrollbar(status_bar_frame, orient=tk.HORIZONTAL, command=text_area.xview)
x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
text_area.config(xscrollcommand=x_scroll.set)

# Create the status bar label
status_text = tk.StringVar()
status_bar = tk.Label(status_bar_frame, textvariable=status_text, anchor='w')
status_bar.pack(side=tk.LEFT, fill=tk.X)
update_status_bar()

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Add file menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Add recent files menu
recent_files_menu = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Recent Files", menu=recent_files_menu)

# Add edit menu
edit_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Undo", command=undo_action)
edit_menu.add_command(label="Redo", command=redo_action)
edit_menu.add_separator()
edit_menu.add_command(label="Cut", command=cut_text)
edit_menu.add_command(label="Copy", command=copy_text)
edit_menu.add_command(label="Paste", command=paste_text)
edit_menu.add_separator()
edit_menu.add_command(label="Select All", command=select_all)
edit_menu.add_command(label="Find and Replace", command=find_text)

# Add view menu
view_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="View", menu=view_menu)
view_menu.add_command(label="Zoom In", command=zoom_in)
view_menu.add_command(label="Zoom Out", command=zoom_out)
view_menu.add_command(label="Default Zoom", command=default_zoom)
view_menu.add_command(label="Toggle Full Screen", command=toggle_full_screen)

# Add selection menu
selection_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Selection", menu=selection_menu)
selection_menu.add_command(label="Select All", command=select_all)
selection_menu.add_command(label="Clear Selection", command=clear_selection)

# Bind Escape key to exit full screen mode
root.bind("<Escape>", exit_full_screen)

# Load and update recent files
recent_files = load_recent_files()
update_recent_files_menu()

# Run the application
root.mainloop()
