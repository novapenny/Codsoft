import tkinter as tk
from PIL import Image, ImageTk
import random

# =============================
# CONFIG
# =============================
WINDOW_SIZE = "620x540"
BG_COLOR = "#FFC107"

CANVAS_WIDTH = 600
CANVAS_HEIGHT = 280

TARGET_SIZE = (150, 150)
BUTTON_SIZE = (100, 100)

LEFT_POS = (180, 140)
RIGHT_POS = (420, 140)

CHOICES = ["rock", "paper", "scissors"]

LEFT_IMAGES = ["rock.jpeg", "paper.jpeg", "scissors.jpeg"]
RIGHT_IMAGES = ["rock_mirror.jpeg", "paper_mirror.jpeg", "scissors_mirror.jpeg"]

# =============================
# INIT
# =============================
root = tk.Tk()
root.title("Rock Paper Scissors")
root.geometry(WINDOW_SIZE)
root.resizable(False, False)
root.configure(bg=BG_COLOR)

canvas = tk.Canvas(
    root,
    width=CANVAS_WIDTH,
    height=CANVAS_HEIGHT,
    bg=BG_COLOR,
    highlightthickness=2,
    highlightbackground="black"
)
canvas.pack(pady=2)

# =============================
# LOAD IMAGES
# =============================
left_imgs = [ImageTk.PhotoImage(Image.open(img).resize(TARGET_SIZE)) for img in LEFT_IMAGES]
right_imgs = [ImageTk.PhotoImage(Image.open(img).resize(TARGET_SIZE)) for img in RIGHT_IMAGES]
btn_imgs = [ImageTk.PhotoImage(Image.open(img).resize(BUTTON_SIZE)) for img in LEFT_IMAGES]

# =============================
# UI ELEMENTS
# =============================
left_hand = canvas.create_image(*LEFT_POS, image=left_imgs[0])
right_hand = canvas.create_image(*RIGHT_POS, image=right_imgs[0])

canvas.create_text(LEFT_POS[0], LEFT_POS[1] - 100, text="PLAYER", font=("Arial", 14, "bold"))
canvas.create_text(RIGHT_POS[0], RIGHT_POS[1] - 100, text="CPU", font=("Arial", 14, "bold"))

# =============================
# GAME STATE
# =============================
player_score = 0
computer_score = 0
max_rounds = 0
current_round = 0

# =============================
# SCORE UI
# =============================
score_frame = tk.Frame(root, bg=BG_COLOR)
score_frame.pack(anchor="w", padx=10)

score_label = tk.Label(
    score_frame,
    text="Player: 0  CPU: 0",
    font=("Arial", 16, "bold"),
    fg="yellow",
    bg="black",
    padx=10,
    pady=5
)
score_label.pack()

# =============================
# START MENU
# =============================
start_frame = tk.Frame(root, bg=BG_COLOR)
start_frame.pack(pady=10)

tk.Label(
    start_frame,
    text="Select Number of Rounds",
    font=("Arial", 18, "bold"),
    bg=BG_COLOR
).pack(pady=5)

# =============================
# FUNCTIONS
# =============================
def reset_hands():
    canvas.coords(left_hand, *LEFT_POS)
    canvas.coords(right_hand, *RIGHT_POS)
    canvas.itemconfig(left_hand, image=left_imgs[0])
    canvas.itemconfig(right_hand, image=right_imgs[0])


def update_score():
    score_label.config(text=f"Player: {player_score}  CPU: {computer_score}")


def disable_buttons():
    for btn in game_buttons:
        btn.config(state="disabled")


def enable_buttons():
    for btn in game_buttons:
        btn.config(state="normal")


def animate_round_text():
    canvas.itemconfig("round_display", fill="red")
    root.after(150, lambda: canvas.itemconfig("round_display", fill="black"))


def shake_hands(callback=None, step=0, steps=24):
    if step < steps:
        dx = 4 if step % 2 == 0 else -4
        dy = 4 if step % 2 == 0 else -4

        canvas.move(left_hand, dx, dy)
        canvas.move(right_hand, -dx, dy)

        root.after(40, shake_hands, callback, step + 1, steps)
    else:
        reset_hands()
        if callback:
            root.after(150, callback)


def reveal_result(player_idx):
    global player_score, computer_score, current_round

    cpu_idx = random.randint(0, 2)

    canvas.itemconfig(left_hand, image=left_imgs[player_idx])
    canvas.itemconfig(right_hand, image=right_imgs[cpu_idx])

    player = CHOICES[player_idx]
    cpu = CHOICES[cpu_idx]

    if player == cpu:
        result = "It's a tie!"
    elif (player == "rock" and cpu == "scissors") or \
         (player == "paper" and cpu == "rock") or \
         (player == "scissors" and cpu == "paper"):
        result = "Player wins!"
        player_score += 1
    else:
        result = "CPU wins!"
        computer_score += 1

    update_score()

    canvas.delete("result")
    canvas.create_text(300, 250, text=result, font=("Arial", 18, "bold"), fill="blue", tags="result")

    current_round += 1
    check_game_state()


def check_game_state():
    wins_needed = max_rounds // 2 + 1

    if player_score >= wins_needed:
        show_winner_popup("PLAYER WINS THE GAME!")
        return
    if computer_score >= wins_needed:
        show_winner_popup("CPU WINS THE GAME!")
        return

    if current_round < max_rounds:
        enable_buttons()
        show_round()
    else:
        if player_score > computer_score:
            text = "PLAYER WINS THE GAME!"
        elif computer_score > player_score:
            text = "CPU WINS THE GAME!"
        else:
            text = "GAME TIED!"
        show_winner_popup(text)


def show_round():
    canvas.delete("round_display")
    canvas.create_text(
        10, 260,
        text=f"Round {current_round + 1} / {max_rounds}",
        font=("Arial", 12, "bold"),
        anchor="w",
        tags="round_display"
    )
    animate_round_text()


def play_round(idx):
    if max_rounds == 0 or current_round >= max_rounds:
        return

    disable_buttons()
    reset_hands()
    canvas.delete("result")
    shake_hands(lambda: reveal_result(idx))


def start_game(rounds):
    global max_rounds, current_round, player_score, computer_score

    max_rounds = rounds
    current_round = 0
    player_score = 0
    computer_score = 0

    update_score()
    show_round()

    start_frame.pack_forget()
    button_frame.pack(pady=30)
    enable_buttons()


def restart_game():
    global player_score, computer_score, current_round, max_rounds

    player_score = computer_score = current_round = max_rounds = 0
    update_score()

    canvas.delete("result")
    canvas.delete("round_display")
    reset_hands()

    button_frame.pack_forget()
    start_frame.pack(pady=10)


def show_winner_popup(text):
    popup = tk.Toplevel(root)
    popup.title("Game Over")

    popup.geometry("300x200")
    popup.resizable(False, False)
    popup.transient(root)
    popup.grab_set()

    tk.Label(popup, text=text, font=("Arial", 16, "bold")).pack(pady=20)

    frame = tk.Frame(popup)
    frame.pack(pady=10)

    tk.Button(frame, text="Play Again", width=10,
              command=lambda: [popup.destroy(), restart_game()]).grid(row=0, column=0, padx=10)

    tk.Button(frame, text="Exit", width=10,
              command=root.destroy).grid(row=0, column=1, padx=10)


# =============================
# BUTTONS
# =============================
tk.Button(start_frame, text="3 Rounds", font=("Arial", 14), command=lambda: start_game(3)).pack(pady=3)
tk.Button(start_frame, text="5 Rounds", font=("Arial", 14), command=lambda: start_game(5)).pack(pady=3)
tk.Button(start_frame, text="9 Rounds", font=("Arial", 14), command=lambda: start_game(9)).pack(pady=3)

button_frame = tk.Frame(root, bg=BG_COLOR)
game_buttons = []

for i, img in enumerate(btn_imgs):
    btn = tk.Button(
        button_frame,
        image=img,
        command=lambda idx=i: play_round(idx),
        bd=4,
        relief="solid",
        highlightthickness=2,
        cursor="hand2"
    )
    btn.grid(row=0, column=i, padx=10)
    game_buttons.append(btn)

# =============================
# RUN
# =============================
root.mainloop()