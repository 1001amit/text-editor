import tkinter as tk
from tkinter import filedialog, font

def new_file():
    text_area.delete(1.0, tk.END)

def open_file():
    file_path = filedialog.askopenfilename(defaultextension=".txt", 
                                           filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, file.read())

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(text_area.get(1.0, tk.END))

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

# Create the main window
root = tk.Tk()
root.title("Simple Text Editor")
root.geometry("800x600")

# Initialize full screen state
is_full_screen = False

# Create a text area
text_font = font.Font(family="Helvetica", size=12)
text_area = tk.Text(root, wrap="word", font=text_font)
text_area.pack(expand=1, fill="both")

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

# Add view menu
view_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="View", menu=view_menu)
view_menu.add_command(label="Zoom In", command=zoom_in)
view_menu.add_command(label="Zoom Out", command=zoom_out)
view_menu.add_command(label="Default Zoom", command=default_zoom)
view_menu.add_command(label="Toggle Full Screen", command=toggle_full_screen)

# Bind Escape key to exit full screen mode
root.bind("<Escape>", exit_full_screen)

# Run the application
root.mainloop()
