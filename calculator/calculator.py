from tkinter import *
import math

# -------------------- APP SETUP -------------------- #

root = Tk()
root.title("Calculator")
root.geometry("320x460")

data = ""
history = []

# -------------------- THEMES -------------------- #

dark_theme = {
    "bg": "#202020",
    "fg": "white",
    "button": "#333333",
    "flash": "#0078D7",
    "equal": "#0078D7"
}

light_theme = {
    "bg": "#f2f2f2",
    "fg": "black",
    "button": "#e0e0e0",
    "flash": "#0078D7",
    "equal": "#0078D7"
}

current_theme = dark_theme

# -------------------- DISPLAY -------------------- #

display_var = StringVar()

display = Entry(
    root,
    textvariable=display_var,
    font=("Segoe UI", 24),
    bd=0,
    justify="right",
    state="readonly",
    readonlybackground=current_theme["bg"],
    fg=current_theme["fg"],
    insertbackground=current_theme["fg"]
)

display.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

# -------------------- CORE FUNCTIONS -------------------- #

def update_display(value):
    display.config(state="normal")
    display_var.set(value)
    display.config(state="readonly")


def press(value):
    global data
    data += str(value)
    update_display(data)


def calculate():
    global data
    try:
        if any(c not in "0123456789+-*/.()" for c in data):
            raise ValueError("Invalid input")

        raw = eval(data)
        result = int(raw) if isinstance(raw, float) and raw == int(raw) else round(raw, 10)

        result = str(result)
        history.append(f"{data} = {result}")

        update_display(result)
        data = result

    except Exception:
        update_display("Error")
        data = ""


def clear():
    global data
    data = ""
    update_display("")


def backspace():
    global data
    data = data[:-1]
    update_display(data)


def square():
    global data
    try:
        result = str(eval(data) ** 2)
        update_display(result)
        data = result
    except Exception:
        update_display("Error")


def sqrt():
    global data
    try:
        result = str(math.sqrt(eval(data)))
        update_display(result)
        data = result
    except Exception:
        update_display("Error")


def percent():
    global data
    try:
        result = str(float(data) / 100)
        update_display(result)
        data = result
    except Exception:
        update_display("Error")

# -------------------- UI EFFECTS -------------------- #

def flash(btn):
    original = btn["bg"]
    btn.config(bg=current_theme["flash"])
    root.after(120, lambda: btn.config(bg=original))

# -------------------- HISTORY -------------------- #

def open_history():
    hist = Toplevel(root)
    hist.title("History")
    hist.geometry("250x300")

    box = Listbox(hist, font=("Segoe UI", 12))
    box.pack(fill=BOTH, expand=True)

    for item in history:
        box.insert(END, item)

# -------------------- KEYBOARD -------------------- #

def key_input(event):
    key = event.char

    if event.keysym == "Return":
        calculate()
    elif event.keysym == "BackSpace":
        backspace()
    elif key and (key.isdigit() or key in "+-*/."):
        press(key)

root.bind("<Key>", key_input)

# -------------------- THEME SYSTEM -------------------- #

def apply_theme(theme):
    global current_theme
    current_theme = theme

    root.config(bg=theme["bg"])

    display.config(
        readonlybackground=theme["bg"],
        fg=theme["fg"],
        insertbackground=theme["fg"]
    )

    for b in buttons:
        b.config(bg=theme["button"], fg=theme["fg"])

    equal_button.config(bg=theme["equal"], fg="white")


def set_dark():
    apply_theme(dark_theme)
    theme_var.set("dark")


def set_light():
    apply_theme(light_theme)
    theme_var.set("light")

# -------------------- MENU -------------------- #

menu_bar = Menu(root)
theme_menu = Menu(menu_bar, tearoff=0)

theme_var = StringVar(value="dark")

theme_menu.add_radiobutton(label="Dark Mode", variable=theme_var, value="dark", command=set_dark)
theme_menu.add_radiobutton(label="Light Mode", variable=theme_var, value="light", command=set_light)

menu_bar.add_cascade(label="Theme", menu=theme_menu)
root.config(menu=menu_bar)

# -------------------- HISTORY BUTTON -------------------- #

history_btn = Button(
    root,
    text="🕘",
    font=("Segoe UI", 12),
    bd=0,
    command=open_history
)

history_btn.grid(row=0, column=0, sticky="w", padx=5)

# -------------------- BUTTON FACTORY -------------------- #

buttons = []

def make_button(text, row, col, cmd):
    b = Button(
        root,
        text=text,
        font=("Segoe UI", 14),
        bd=0,
        width=5,
        height=2
    )

    def action():
        flash(b)
        cmd()

    b.config(command=action)
    b.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    buttons.append(b)

# -------------------- BUTTON LAYOUT -------------------- #

make_button("C", 1, 0, clear)
make_button("⌫", 1, 1, backspace)
make_button("%", 1, 2, percent)
make_button("√", 1, 3, sqrt)

make_button("7", 2, 0, lambda: press(7))
make_button("8", 2, 1, lambda: press(8))
make_button("9", 2, 2, lambda: press(9))
make_button("÷", 2, 3, lambda: press("/"))

make_button("4", 3, 0, lambda: press(4))
make_button("5", 3, 1, lambda: press(5))
make_button("6", 3, 2, lambda: press(6))
make_button("×", 3, 3, lambda: press("*"))

make_button("1", 4, 0, lambda: press(1))
make_button("2", 4, 1, lambda: press(2))
make_button("3", 4, 2, lambda: press(3))
make_button("-", 4, 3, lambda: press("-"))

make_button("0", 5, 0, lambda: press(0))
make_button(".", 5, 1, lambda: press("."))
make_button("x²", 5, 2, square)
make_button("+", 5, 3, lambda: press("+"))

# -------------------- EQUAL BUTTON -------------------- #

def equal_action():
    flash(equal_button)
    calculate()

equal_button = Button(
    root,
    text="=",
    command=equal_action,
    font=("Segoe UI", 16),
    bd=0
)

equal_button.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=5, pady=10)

# -------------------- GRID CONFIG -------------------- #

for i in range(7):
    root.rowconfigure(i, weight=1)

for i in range(4):
    root.columnconfigure(i, weight=1)

# -------------------- INIT -------------------- #

apply_theme(dark_theme)

root.mainloop()