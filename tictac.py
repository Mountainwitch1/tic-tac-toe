import tkinter as tk
from tkinter import messagebox
import random
import threading
import pygame



pygame.mixer.init()

def play_sound(path):
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Error playing sound: {e}")

# ----------- Global Variables -----------

board = [["" for _ in range(3)] for _ in range(3)]
buttons = [[None for _ in range(3)] for _ in range(3)]
current_player = "X"
is_vs_ai = True
ai_difficulty = "Impossible"
player_names = {"X": "Player 1", "O": "Computer"}
scores = {"X": 0, "O": 0, "Draw": 0}

TIMER_DURATION = 10
timer_label = None
timer = None
time_left = TIMER_DURATION

#sound
CLICK_SOUND = "click.wav"
WIN_SOUND = "win.wav"
DRAW_SOUND = "draw.wav"

# ----------- AI Logic -----------

def ai_easy():
    empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    return random.choice(empty)

def ai_medium():
    for player in ["O", "X"]:
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = player
                    if check_winner(player):
                        board[r][c] = ""
                        return (r, c)
                    board[r][c] = ""
    return ai_easy()

def minimax(board_state, is_maximizing):
    winner = evaluate(board_state)
    if winner is not None:
        return winner

    scores = []
    for r in range(3):
        for c in range(3):
            if board_state[r][c] == "":
                board_state[r][c] = "O" if is_maximizing else "X"
                score = minimax(board_state, not is_maximizing)
                board_state[r][c] = ""
                scores.append(score)

    return max(scores) if is_maximizing else min(scores)

def evaluate(board_state):
    for p in ["X", "O"]:
        if any(
            all(board_state[i][j] == p for j in range(3)) or
            all(board_state[j][i] == p for j in range(3)) or
            all(board_state[j][j] == p for j in range(3)) or
            all(board_state[j][2-j] == p for j in range(3))
            for i in range(3)
        ):
            return 1 if p == "O" else -1
    if all(cell != "" for row in board_state for cell in row):
        return 0
    return None

def best_move():
    best_score = float('-inf')
    move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = "O"
                score = minimax(board, False)
                board[r][c] = ""
                if score > best_score:
                    best_score = score
                    move = (r, c)
    return move

def get_ai_move():
    if ai_difficulty == "Easy":
        return ai_easy()
    elif ai_difficulty == "Medium":
        return ai_medium()
    else:
        return best_move()

# ----------- Game Logic -----------

def check_winner(player):
    for i in range(3):
        if all(board[i][j] == player for j in range(3)) or \
           all(board[j][i] == player for j in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)) or \
       all(board[i][2 - i] == player for i in range(3)):
        return True
    return False

def is_draw():
    return all(cell != "" for row in board for cell in row)

def update_scores_display():
    score_label.config(text=f"{player_names['X']}: {scores['X']}  |  "
                            f"{player_names['O']}: {scores['O']}  |  "
                            f"Draws: {scores['Draw']}")

def reset_game():
    global board, current_player
    board = [["" for _ in range(3)] for _ in range(3)]
    current_player = "X"
    for r in range(3):
        for c in range(3):
            buttons[r][c].config(text="", state="normal")
    start_timer()

def make_move(row, col, player):
    global current_player
    if board[row][col] == "":
        play_sound(CLICK_SOUND)
        board[row][col] = player
        emoji = "❌" if player == "X" else "⭕"
        buttons[row][col].config(text=emoji, state="disabled")

        if check_winner(player):
            play_sound(WIN_SOUND)
            messagebox.showinfo("Game Over", f"{emoji} {player_names[player]} wins!")
            scores[player] += 1
            update_scores_display()
            root.after_cancel(timer)
            rematch()
        elif is_draw():
            play_sound(DRAW_SOUND)
            messagebox.showinfo("Game Over", "🤝 It's a draw!")
            scores["Draw"] += 1
            update_scores_display()
            root.after_cancel(timer)
            rematch()
        else:
            current_player = "O" if player == "X" else "X"
            start_timer()
            if is_vs_ai and current_player == "O":
                root.after(300, ai_turn)

def ai_turn():
    r, c = get_ai_move()
    make_move(r, c, "O")

def on_click(row, col):
    if not is_vs_ai or current_player == "X":
        make_move(row, col, current_player)

# ----------- Timer Logic -----------

def start_timer():
    global time_left, timer
    time_left = TIMER_DURATION
    update_timer()
    if timer:
        root.after_cancel(timer)
    count_down()

def update_timer():
    timer_label.config(text=f"⏳ {time_left}s left")

def count_down():
    global time_left, timer
    if time_left > 0:
        update_timer()
        time_left -= 1
        timer = root.after(1000, count_down)
    else:
        update_timer()
        handle_time_out()

def handle_time_out():
    global current_player
    messagebox.showinfo("⏰ Time's up!", f"{player_names[current_player]} took too long!")
    if is_vs_ai and current_player == "X":
        current_player = "O"
        ai_turn()
    elif not is_vs_ai:
        current_player = "O" if current_player == "X" else "X"
    start_timer()

# ----------- Rematch Logic -----------

def rematch():
    global board, current_player
    board = [["" for _ in range(3)] for _ in range(3)]
    current_player = "X"
    for r in range(3):
        for c in range(3):
            buttons[r][c].config(text="", state="normal")
    start_timer()

# ----------- Mode Toggle -----------

def toggle_mode():
    global is_vs_ai
    is_vs_ai = not is_vs_ai
    player_names["O"] = "Computer" if is_vs_ai else "Player 2"
    mode_btn.config(text="Mode: 1P vs AI" if is_vs_ai else "Mode: 2P")
    update_scores_display()
    reset_game()

def set_difficulty(level):
    global ai_difficulty
    ai_difficulty = level
    difficulty_label.config(text=f"Difficulty: {ai_difficulty}")
    reset_game()

def set_player_names():
    name1 = name_entry1.get().strip() or "Player 1"
    name2 = name_entry2.get().strip() or ("Computer" if is_vs_ai else "Player 2")
    player_names["X"] = name1
    player_names["O"] = name2
    update_scores_display()
    name_entry1.config(state="disabled")
    name_entry2.config(state="disabled")
    start_btn.config(state="disabled")
    start_timer()

# ----------- GUI Setup -----------

root = tk.Tk()
root.title("Ultimate Tic Tac Toe 🎮")

# Name entries
tk.Label(root, text="Player 1 Name:").grid(row=0, column=0)
name_entry1 = tk.Entry(root)
name_entry1.grid(row=0, column=1)

tk.Label(root, text="Player 2 / AI Name:").grid(row=1, column=0)
name_entry2 = tk.Entry(root)
name_entry2.grid(row=1, column=1)

start_btn = tk.Button(root, text="Start Game", command=set_player_names)
start_btn.grid(row=0, column=2, rowspan=2)

# Game grid
for r in range(3):
    for c in range(3):
        btn = tk.Button(root, text="", font=("Helvetica", 40), width=4, height=2,
                        command=lambda r=r, c=c: on_click(r, c))
        btn.grid(row=r+2, column=c)
        buttons[r][c] = btn

# Mode & Difficulty
mode_btn = tk.Button(root, text="Mode: 1P vs AI", command=toggle_mode)
mode_btn.grid(row=5, column=0)

difficulty_label = tk.Label(root, text=f"Difficulty: {ai_difficulty}")
difficulty_label.grid(row=5, column=1)

difficulty_menu = tk.OptionMenu(root, tk.StringVar(value=ai_difficulty),
                                "Easy", "Medium", "Impossible", command=set_difficulty)
difficulty_menu.grid(row=5, column=2)

# Timer Display
timer_label = tk.Label(root, text=f"⏳ {TIMER_DURATION}s left", font=("Helvetica", 12))
timer_label.grid(row=6, column=0, columnspan=3)

# Rematch Button
rematch_btn = tk.Button(root, text="🔁 Rematch", command=rematch)
rematch_btn.grid(row=7, column=0, columnspan=3)

# Score Display
score_label = tk.Label(root, text="Scoreboard", font=("Helvetica", 12, "bold"))
score_label.grid(row=8, column=0, columnspan=3)
update_scores_display()

root.mainloop()
