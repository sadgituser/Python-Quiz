import tkinter as tk
from tkinter import *
import sys
import os
from tkinter import font, messagebox, filedialog
import webbrowser
import random
import time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import stateVars
import quiz_defs

# Early definitions
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, "Assets", relative_path)


# Variables
background_colour, foreground_colour = "#000000", "#00FF00"
active_background_colour, active_foreground_colour = "#00CC00", "#000000"
rootWidth, rootHeight = 800, 700
app_icon = resource_path("app-icon.ico")
mainFontFamily = "Consolas"
bg_music_path = resource_path("bg_music.mp3")
players = []
questions = []
print_queue = []
is_printing = False
quiz_ready = False
quiz_settings = {
    "rand_questions": False,
    "rand_players": False,
    "time_limit": 15,
    "default_skips": 2,
    "default_last_chance": True
}
quiz_active_players = []
quiz_active_questions = []
current_player_idx = 0
current_question_idx = 0
current_timer_id = None
time_remaining = 0
waiting_for_next = False
is_paused = False
is_last_chance_action = False
intro_timer_id = None


# Music (initialise)
pygame.mixer.init()


# Initialise main window
stateVars.stateVars.root=tk.Tk()
stateVars.stateVars.root.title("Quiz")
stateVars.stateVars.root.geometry(f"{rootWidth}x{rootHeight}+100+100")
stateVars.stateVars.root.resizable(False, False)
stateVars.stateVars.root.configure(bg=background_colour)
try:
    stateVars.stateVars.root.iconbitmap(app_icon)
except:
    pass


# CRT Effect
stateVars.stateVars.crt_canvas = tk.Canvas(stateVars.stateVars.root, width=rootWidth, height=rootHeight, bg=background_colour, highlightthickness=0)
stateVars.stateVars.crt_canvas.place(x=0, y=0, relwidth=1, relheight=1)

# Scan Lines
for y in range(0, rootHeight, 3):
    stateVars.stateVars.crt_canvas.create_line(0, y, rootWidth, y, fill="#001100", stipple="gray50", tags="scanlines")

# Moving Scanline
moving_scanline = stateVars.stateVars.crt_canvas.create_line(0, 0, rootWidth, 0, fill="#00FF44", width=10, stipple="gray25")
scanline_y = 0

def animate_crt_beam():
    global scanline_y
    scanline_y += 3
    if scanline_y > rootHeight:
        scanline_y = 0
    stateVars.stateVars.crt_canvas.coords(moving_scanline, 0, scanline_y, rootWidth, scanline_y)
    stateVars.stateVars.root.after(20, animate_crt_beam)
animate_crt_beam()


# CRT Flicker
def apply_crt_flicker():
    glow_colours = ["#00FF00", "#00DD00", "#22FF22", "#00EE00"]
    chosen_colour = random.choice(glow_colours)
    titleLabel.configure(fg=chosen_colour)
    termText.configure(fg=chosen_colour)
    termEntry.configure(fg=chosen_colour)
    stateVars.stateVars.root.after(random.randint(60, 180), apply_crt_flicker)


# Fonts
titleFont = font.Font(family=mainFontFamily, size=28, underline=True, weight="bold")
descFont = font.Font(family=mainFontFamily, size=14)
buttonFont = font.Font(family=mainFontFamily, size=17, underline=True)
playerFont = font.Font(family=mainFontFamily, size=48, weight="bold", underline=True)
questionFont = font.Font(family=mainFontFamily, size=24, weight="bold")
timerFont = font.Font(family=mainFontFamily, size=18, weight="bold")
statusFont = font.Font(family=mainFontFamily, size=17)
winnerFont = font.Font(family=mainFontFamily, size=48, underline=True, weight="bold")


# Widgets
titleLabel = tk.Label(stateVars.stateVars.root,
    text="THE CRT",
    font=titleFont,
    bg=background_colour,
    fg=foreground_colour,
    wraplength=(rootWidth-25),
    justify="center"
)
titleLabel.place(x=(rootWidth // 2), y=20, anchor="n")

# Clock
clockLabel = tk.Label(stateVars.stateVars.root,
    font=descFont,
    bg=background_colour,
    fg=foreground_colour
)
clockLabel.place(x=(rootWidth - 15), y=20, anchor="ne")

def update_clock():
    current_time = time.strftime("%H:%M:%S")
    clockLabel.config(text=current_time)
    stateVars.stateVars.root.after(500, update_clock)
update_clock()


# Gamble
def testLuck():
    luckPopup = tk.Toplevel(stateVars.stateVars.root)
    luckPopup.title("TEST YOUR LUCK...")
    luckPopup.geometry("300x300+150+150")
    luckPopup.resizable(False, False)
    luckPopup.configure(bg=background_colour)
    try:
        luckPopup.iconbitmap(app_icon)
    except:
        pass

    currentLuck = "FAIL!"

    luckLabel = tk.Label(luckPopup,
        text=currentLuck,
        font=titleFont,
        bg=background_colour,
        fg=foreground_colour,
        wraplength=250,
        justify="center"
    )
    luckLabel.place(x=150, y=125, anchor="n")

    def spin_luck():
        nonlocal currentLuck
        currentLuck = "WIN!" if currentLuck == "FAIL!" else "FAIL!"
        luckLabel.configure(text=currentLuck)
    
    currentRanNum = random.randint(5, 25)

    for i in range(currentRanNum):
        luckPopup.after(i * 100, spin_luck)

    def finish_luck():
        if currentLuck == "FAIL!":
            messagebox.showerror("You Failed", "You lost the gamble...")
            luckPopup.destroy()
            stateVars.stateVars.root.destroy()
        else:
            messagebox.showinfo("You Win", "Your gamble paid off! You get...")
            messagebox.showinfo("Nothing", "NOTHING! :o")
            luckPopup.destroy()

    luckPopup.after(((currentRanNum * 100) + 100), finish_luck)


def openMePages():
    webbrowser.open_new("https://github.com/sadgituser")
    webbrowser.open_new_tab("https://theprintedcraftuk.etsy.com")
    webbrowser.open_new_tab("mailto:kavi@mistrypi.dev")


# Terminal Output Box
termText = tk.Text(stateVars.stateVars.root, 
    bg="#000500", 
    fg=foreground_colour, 
    insertbackground=foreground_colour, 
    font=descFont, 
    relief="flat"
)
termText.place(x=15, y=80, width=(rootWidth - 30), height=(rootHeight - 150))
termText.insert("end", "CRT OS v1.0\nType 'help' for commands. \n\n> ")
termText.config(state="disabled")

# Terminal Entry
promptLabel = tk.Label(stateVars.root, 
    text=">",
    font=descFont,
    bg=background_colour,
    fg=foreground_colour
)
promptLabel.place(x=15, y=(rootHeight - 55))

termEntry = tk.Entry(stateVars.root,
    bg=background_colour,
    fg=foreground_colour,
    insertbackground=foreground_colour,
    font=descFont,
    relief="flat",
    highlightthickness=1,
    highlightbackground=foreground_colour
)
termEntry.place(x=35, y=(rootHeight - 55), width=(rootWidth - 50), height=30)
termEntry.focus()


quizPlayerLabel = tk.Label(stateVars.root, 
    font=playerFont, 
    bg=background_colour, 
    fg=foreground_colour, 
    justify="center"
)
quizQuestionLabel = tk.Label(stateVars.root, 
    font=questionFont, 
    bg=background_colour, 
    fg=foreground_colour, 
    wraplength=(rootWidth - 50), 
    justify="center"
)
quizTimerLabel = tk.Label(stateVars.root, 
    font=timerFont, 
    bg=background_colour, 
    fg=foreground_colour, 
    justify="center"
)
quizStatusLabel = tk.Label(stateVars.root, 
    font=statusFont, 
    bg=background_colour, 
    fg=foreground_colour, 
    justify="center"
)


# Print to the Terminal
def process_print_queue():
    global is_printing
    if not print_queue:
        is_printing = False
        return

    is_printing = True
    text_to_print = print_queue.pop(0)

    termText.config(state="normal")
    termText.insert("end", "\n")
    termText.config(state="disabled")

    def type_chars(remaining_text):
        termText.config(state="normal")
        if remaining_text:
            termText.insert("end", remaining_text[0])
            termText.see("end")
            termText.config(state="disabled")
            stateVars.root.after(25, lambda: type_chars(remaining_text[1:]))
        else:
            termText.config(state="normal")
            if print_queue:
                pass
            else:
                termText.insert("end", "\n> ")
            termText.see("end")
            termText.config(state="disabled")
            process_print_queue()

    stateVars.root.after(100, lambda: type_chars(text_to_print))

def print_term(text):
    global is_printing
    print_queue.append(text)
    if not is_printing:
        process_print_queue()


# Terminal Commands
def clear_term():
    termText.config(state="normal")
    termText.delete("1.0", "end")
    termText.config(state="disabled")
    print_term("")

def load_playerlist():
    global players
    filepath = filedialog.askopenfilename(title = "Select the playerlist.txt file!", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if filepath:
        try:
            with open(filepath, "r") as f:
                players = [line.strip() for line in f if line.strip()]
            print_term(f"Successfully loaded {len(players)} players! \n")
        except Exception as e:
            print_term(f"Failed to load player list: {e} \n")

def load_questionlist():
    global questions
    filepath = filedialog.askopenfilename(title="Select the questionslist.txt file!", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if filepath:
        try:
            with open(filepath, "r") as f:
                questions = [line.strip() for line in f if line.strip()]
            print_term(f"Successfully loaded {len(questions)} questions! \n")
        except Exception as e:
            print_term(f"Failed to load question list: {e} \n")

def show_playerlist():
    if not players:
        print_term("No players loaded! Use 'quiz player load' first! \n")
    else:
        player_output = "Player List:\n\n"
        for player in players:
            player_output += f"- {player}\n"
        print_term(player_output.strip())

def show_questionlist():
    if not questions:
        print_term("No questions loaded! Use 'quiz question load' first! \n")
    else:
        question_output = "Question List:\n\n"
        for q in questions:
            question_output += f"- {q}\n"
        print_term(question_output.strip())

def preface_quiz():
    global quiz_ready
    msg = "Checking quiz requirements... \n"
    if questions and players:
        msg += "Questions and players loaded... \nQuiz ready\n"
        quiz_ready = True
    elif questions and not players:
        msg += "Questions loaded \nPlayers still to be loaded, load players with 'quiz player load'\n"
        quiz_ready = False
    elif players and not questions:
        msg += "Players loaded \nQuestions still to be loaded, load questions with 'quiz question load'\n"
        quiz_ready = False
    else:
        msg += "Nothing loaded \nPlease load files by typing 'quiz player load' and 'quiz question load'\n"
        quiz_ready = False
    print_term(msg)

def show_syntax():
    syn = "To use basic commands (such as 'rickroll' or 'exit'), just type the command. For more complex commands like 'quiz', type in 'quiz', followed by a space and then the next command suggested by 'Available commands'"
    print_term(syn)


# Quiz Components
quiz_setup_step = 0

def start_quiz_setup():
    global quiz_ready, quiz_setup_step
    if quiz_ready == False:
        print_term("Run 'quiz preface' first\n")
        return
    quiz_setup_step = 1
    print_term("-- QUIZ SETTINGS INITIALISATION --\nRandomise question order? (y/n):")

winner_flashing = False
winner_timer_id = None
winner_can_exit = False

def toggle_pause():
    global is_paused, current_timer_id
    if waiting_for_next:
        return

    is_paused = not is_paused
    if is_paused:
        if current_timer_id:
            stateVars.root.after_cancel(current_timer_id)
            current_timer_id = None
        quizPauseButton.config(text="RESUME")
    else:
        quizPauseButton.config(text="PAUSE")
        current_timer_id = stateVars.root.after(1000, update_quiz_timer)

def force_quit_quiz():
    global current_timer_id, quiz_setup_step, waiting_for_next, is_paused, intro_timer_id
    if current_timer_id:
        stateVars.root.after_cancel(current_timer_id)
        current_timer_id = None
    if intro_timer_id:
        stateVars.root.after_cancel(intro_timer_id)
        intro_timer_id = None
    waiting_for_next = False
    is_paused = False
    quiz_setup_step = 0
    stateVars.root.unbind("<Key>")
    reset_screen_colours()
    quizPlayerLabel.place_forget()
    quizQuestionLabel.place_forget()
    quizTimerLabel.place_forget()
    quizStatusLabel.place_forget()
    quizPauseButton.place_forget()
    quizQuitButton.place_forget()
    titleLabel.place(x=(rootWidth // 2), y=20, anchor="n")
    stateVars.crt_canvas.itemconfigure(moving_scanline, state="normal")
    pygame.mixer.music.set_volume(0.3)
    show_terminal_from_quiz()
    print_term("Quiz force quit by user.\n")

quizPauseButton = tk.Button(stateVars.root,
    text="PAUSE",
    font=descFont,
    bg=background_colour,
    fg=foreground_colour,
    relief="solid",
    command=toggle_pause
)
quizQuitButton = tk.Button(stateVars.root,
    text="QUIT QUIZ",
    font=descFont,
    bg=background_colour,
    fg="#FF0000",
    relief="solid",
    command=force_quit_quiz
)


def load_default_players():
    global players
    players = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5", "Player 6", "Player 7", "Player 8", "Player 9", "Player 10"]
    print_term(f"Loaded {len(players)} default players! \n")

def load_default_questions():
    global questions
    questions = ["What is the largest mammal on Earth?", 
        "Who wrote 'Romeo and Juliet'?", 
        "What is the chemical symbol for gold?", 
        "Which ocean is the largest?", 
        "What is 12 x 8?", 
        "Who painted the Mona Lisa?", 
        "What is the boiling point of water in degrees Celsius?", 
        "Which country is home to the Great Pyramid of Giza?", 
        "What is the fastest land animal?", 
        "Who invented the telephone?", 
        "What is the square stateVars.root of 144?", 
        "Which gas do plants absorb from the atmosphere?", 
        "What is the smallest prime number?", 
        "Who was the first person to walk on the Moon?", 
        "Which continent is the Sahara Desert located on?", 
        "What is the capital of Japan?", 
        "How many bones are in the adult human body?", 
        "Which planet is closest to the Sun?", 
        "What is the hardest natural substance?", 
        "Who discovered gravity after observing a falling apple?", 
        "What is the largest continent?", 
        "How many days are there in a leap year?", 
        "What is the currency of the United Kingdom?", 
        "Which element has the chemical symbol O?", 
        "What is the tallest mountain in the world?", 
        "Who wrote 'Harry Potter'?", 
        "How many colours are there in a rainbow?", 
        "What is the capital city of Australia?", 
        "Which bird is often associated with delivering babies in stories?", 
        "What is the freezing point of water in degrees Celsius?", 
        "Which organ pumps blood around the human body?", 
        "What is the longest river in the world?", 
        "Who painted the ceiling of the Sistine Chapel?", 
        "Which country invented pizza?", 
        "What is the largest planet in the Solar System?", 
        "How many minutes are in one hour?", 
        "What is the chemical symbol for silver?", 
        "Who was the first President of the United States?", 
        "What is the capital of Canada?", 
        "Which instrument has 88 keys?", 
        "What is the tallest animal in the world?", 
        "Which planet has rings that are clearly visible from Earth?", 
        "What is the primary language spoken in Brazil?", 
        "What is 15 squared?", 
        "Who wrote 'The Hobbit'?", 
        "Which metal is liquid at room temperature?", 
        "What is the largest species of shark?", 
        "What is the national sport of Japan?", 
        "Which country is famous for the Eiffel Tower?", 
        "What is the value of Pi rounded to two decimal places?", 
        "How many continents are there on Earth?", 
        "What is the largest desert in the world?", 
        "Who developed the theory of relativity?", 
        "What is the capital of Spain?", 
        "Which planet is known for its Great Red Spot?", 
        "What is the name of the galaxy that contains our Solar System?", 
        "How many players are on a standard football (soccer) team on the field?", 
        "What is the world's most abundant gas?", 
        "Who painted 'Starry Night'?", 
        "What is the capital of Germany?", 
        "How many strings does a standard guitar have?"]
    print_term(f"Loaded {len(questions)} default questions! \n")

def handle_quiz_setup_input(raw_cmd):
    global quiz_setup_step, quiz_settings
    if quiz_setup_step == 1:
        quiz_settings['rand_questions'] = (raw_cmd == 'y')
        quiz_setup_step = 2
        print_term("Randomise player order? (y/n):")
    elif quiz_setup_step == 2:
        quiz_settings['rand_players'] = (raw_cmd == 'y')
        quiz_setup_step = 3
        print_term("Enter time limit per question (seconds - applies to all questions):")
    elif quiz_setup_step == 3:
        try:
            quiz_settings['time_limit'] = int(raw_cmd)
        except ValueError:
            quiz_settings['time_limit'] = 15
        quiz_setup_step = 4
        print_term("Enter default skips allowed per player:")
    elif quiz_setup_step == 4:
        try:
            quiz_settings['default_skips'] = int(raw_cmd)
        except ValueError:
            quiz_settings['default_skips'] = 2
        quiz_setup_step = 5
        print_term("Enable default last chance on timeout? (y/n):")
    elif quiz_setup_step == 5:
        quiz_settings['default_last_chance'] = (raw_cmd == 'y')
        quiz_setup_step = 0
        print_term("Settings applied. Starting quiz...\n")
        begin_quiz_execution()

def begin_quiz_execution():
    global quiz_active_players, quiz_active_questions, current_player_idx, current_question_idx

    pygame.mixer.music.set_volume(0.1)

    quiz_active_players = [{
        "name": p,
        "skips": quiz_settings['default_skips'],
        "eliminated": False,
        "last_chance": False
    } for p in players]

    if quiz_settings['rand_players']:
        random.shuffle(quiz_active_players)

    quiz_active_questions = list(questions)
    if quiz_settings['rand_questions']:
        random.shuffle(quiz_active_questions)

    current_player_idx = 0
    current_question_idx = 0

    hide_terminal_for_quiz()
    show_next_quiz_turn()

def hide_terminal_for_quiz():
    termText.place_forget()
    promptLabel.place_forget()
    termEntry.place_forget()
    stateVars.crt_canvas.itemconfigure("scanlines", state="hidden")
    stateVars.crt_canvas.itemconfigure(moving_scanline, state="hidden")
    stateVars.root.focus_set()

def show_terminal_from_quiz():
    termText.place(x=15, y=80, width=(rootWidth - 30), height=(rootHeight - 200))
    promptLabel.place(x=15, y=(rootHeight - 55))
    termEntry.place(x=35, y=(rootHeight - 55), width=(rootWidth - 50), height=30)
    stateVars.crt_canvas.itemconfigure("scanlines", state="normal")
    stateVars.crt_canvas.itemconfigure(moving_scanline, state="normal")
    termEntry.focus()

def show_next_quiz_turn():
    global current_player_idx, current_question_idx, time_remaining, current_timer_id, waiting_for_next, is_paused, intro_timer_id
    waiting_for_next = False
    is_paused = False

    if intro_timer_id:
        stateVars.root.after_cancel(intro_timer_id)
        intro_timer_id = None
    if current_timer_id:
        stateVars.root.after_cancel(current_timer_id)
        current_timer_id = None


    quizPauseButton.config(text="PAUSE")

    active_remaining = [p for p in quiz_active_players if not p['eliminated']]
    if len(active_remaining) == 1:
        show_winner_screen(active_remaining[0]["name"])
        return
    elif not active_remaining:
        end_quiz("Quiz Over! All players eliminated!")
        return

    if current_question_idx >= len(quiz_active_questions):
        current_question_idx = 0
        if quiz_settings['rand_questions']:
            random.shuffle(quiz_active_questions)

    while quiz_active_players[current_player_idx]['eliminated']:
        current_player_idx = (current_player_idx + 1) % len(quiz_active_players)

    player = quiz_active_players[current_player_idx]

    titleLabel.place_forget()
    quizQuestionLabel.place_forget()
    quizTimerLabel.place_forget()
    quizPauseButton.place_forget()
    quizQuitButton.place_forget()

    quizPlayerLabel.config(text=player['name'], fg=foreground_colour, font=playerFont)
    quizPlayerLabel.place(x=(rootWidth // 2), y=30, anchor="n")

    status_text = f"Skips Left: {player['skips']}"
    if quiz_settings['default_last_chance']:
        status_text += f" | Last Chance: {'FINAL CHANCE' if player['last_chance'] else 'NO'}"
    quizStatusLabel.config(text=status_text, fg=foreground_colour, font=statusFont)
    quizStatusLabel.place(x=(rootWidth // 2), y=150, anchor="n")


    stateVars.root.unbind("<Key>")
    stateVars.root.after(3000, start_actual_question)

def start_actual_question():
    global current_timer_id, time_remaining
    player = quiz_active_players[current_player_idx]
    question = quiz_active_questions[current_question_idx]

    quizPlayerLabel.config(text=player['name'], fg=foreground_colour, font=playerFont)
    quizPlayerLabel.place(x=(rootWidth // 2), y=15, anchor="n")
    quizQuestionLabel.config(text=question, fg=foreground_colour, font=questionFont)
    quizQuestionLabel.place(x=(rootWidth // 2), y=120, anchor="n")

    status_text = f"Skips Left: {player['skips']}"
    if quiz_settings['default_last_chance']:
        status_text += f" | Last Chance: {'FINAL CHANCE' if player['last_chance'] else 'NO'}"
    quizStatusLabel.config(text=status_text, fg=foreground_colour, font=statusFont)
    quizStatusLabel.place(x=(rootWidth // 2), y=330, anchor="n")

    if current_timer_id:
        stateVars.root.after_cancel(current_timer_id)
        current_timer_id = None

    time_remaining = quiz_settings['time_limit']
    quizTimerLabel.config(text=f"Time: {time_remaining}s", fg=foreground_colour, font=timerFont)
    quizTimerLabel.place(x=(rootWidth // 2), y=410, anchor="n")

    quizPauseButton.place(x=(rootWidth // 2) - 110, y=500, width=100, height=40)
    quizQuitButton.place(x=(rootWidth // 2) + 10, y=500, width=100, height=40)

    stateVars.root.bind("<Key>", handle_quiz_keypress)
    current_timer_id = stateVars.root.after(1000, update_quiz_timer)

def update_quiz_timer():
    global time_remaining, current_timer_id, waiting_for_next, is_paused
    if waiting_for_next or is_paused:
        return
    if time_remaining > 0:
        time_remaining -= 1
        quizTimerLabel.config(text=f"Time: {time_remaining}s")
        current_timer_id = stateVars.root.after(1000, update_quiz_timer)
    else:
        handle_timeout()

def handle_timeout():
    player = quiz_active_players[current_player_idx]
    flash_screen("#FFA500", "TIME OUT")
    if quiz_settings['default_last_chance'] and not player['last_chance']:
        player['last_chance'] = True
    else:
        player['eliminated'] = True
    prepare_for_next_turn()

def flash_screen(colour, message):
    global waiting_for_next, current_timer_id
    waiting_for_next = True
    if current_timer_id:
        stateVars.root.after_cancel(current_timer_id)
        current_timer_id = None

    stateVars.root.configure(bg=colour)
    stateVars.crt_canvas.configure(bg=colour)
    quizPlayerLabel.config(bg=colour, fg="#000000")
    quizQuestionLabel.config(bg=colour, fg="#000000", font=winnerFont)
    quizTimerLabel.config(bg=colour, fg="#000000")
    quizStatusLabel.config(bg=colour, fg="#000000")
    quizPauseButton.place_forget()
    quizQuitButton.place_forget()

    quizQuestionLabel.config(text=message)

def prepare_for_next_turn():
    global waiting_for_next
    waiting_for_next = True

def reset_screen_colours():
    stateVars.root.configure(bg=background_colour)
    stateVars.crt_canvas.configure(bg=background_colour)
    quizPlayerLabel.config(bg=background_colour, fg=foreground_colour, font=playerFont)
    quizQuestionLabel.config(bg=background_colour, fg=foreground_colour, font=questionFont)
    quizTimerLabel.config(bg=background_colour, fg=foreground_colour, font=timerFont)
    quizStatusLabel.config(bg=background_colour, fg=foreground_colour, font=statusFont)

def handle_quiz_keypress(event):
    global current_player_idx, current_question_idx, time_remaining, current_timer_id, waiting_for_next, is_last_chance_action
    player = quiz_active_players[current_player_idx]
    key = event.char.lower()

    if waiting_for_next:
        if key == 'n':
            reset_screen_colours()
            if is_last_chance_action:
                is_last_chance_action = False
                waiting_for_next = False
                quizPlayerLabel.config(text=player['name'], fg=foreground_colour, font=playerFont)
                quizPlayerLabel.place(x=(rootWidth // 2), y=15, anchor="n")
                quizQuestionLabel.config(text=quiz_active_questions[current_question_idx], fg=foreground_colour, font=questionFont)
                quizQuestionLabel.place(x=(rootWidth // 2), y=120, anchor="n")

                status_text = f"Skips Left: {player['skips']}"
                if quiz_settings['default_last_chance']:
                    status_text += f" | Last Chance: {'FINAL CHANCE' if player['last_chance'] else 'NO'}"
                quizStatusLabel.config(text=status_text, fg=foreground_colour, font=statusFont)
                quizStatusLabel.place(x=(rootWidth // 2), y=330, anchor="n")

                quizTimerLabel.config(text=f"Time Remaining: {time_remaining}s", fg=foreground_colour, font=timerFont)
                quizTimerLabel.place(x=(rootWidth // 2), y=410, anchor="n")

                quizPauseButton.place(x=(rootWidth // 2) - 100, y=500, width=100, height=40)
                quizQuitButton.place(x=(rootWidth // 2 + 10), y=500, width=100, height=40)

                stateVars.root.bind("<Key>", handle_quiz_keypress)
                if current_timer_id:
                    stateVars.root.after_cancel(current_timer_id)
                current_timer_id = stateVars.root.after(1000, update_quiz_timer)
            else:
                quizPlayerLabel.place_forget()
                quizQuestionLabel.place_forget()
                quizTimerLabel.place_forget()
                quizStatusLabel.place_forget()
                quizPauseButton.place_forget()
                quizQuitButton.place_forget()
                titleLabel.place(x=(rootWidth // 2), y=20, anchor="n")

                current_question_idx += 1
                current_player_idx = (current_player_idx + 1) % len(quiz_active_players)
                show_next_quiz_turn()
            return "break"


    if current_timer_id:
        stateVars.root.after_cancel(current_timer_id)
        current_timer_id = None

    if key == 'y':
        flash_screen("#00FF00", "CORRECT")
        prepare_for_next_turn()
    elif key == 'i':
        if quiz_settings['default_last_chance'] and not player['last_chance']:
            player['last_chance'] = True
            flash_screen("#8B0000", "INCORRECT & LAST CHANCE")
        else:
            player['eliminated'] = True
            flash_screen("#8B0000", "INCORRECT & ELIMINATED")
        prepare_for_next_turn()
    elif key == 'p':
        if player['skips'] > 0:
            player['skips'] -= 1
            flash_screen("#FFFFFF", "SKIPPED")
            prepare_for_next_turn()
    elif key == 'q':
        if quiz_settings['default_last_chance'] and not player['last_chance']:
            player['skips'] = 0
            player['last_chance'] = True
            time_remaining += 5
            is_last_chance_action = True
            quizTimerLabel.config(text=f"Time: {time_remaining}s")
            flash_screen("#8B0000", "LAST CHANCE TRIGGERED")

    return "break"

def show_winner_screen(winner_name):
    global waiting_for_next, winner_flashing, winner_timer_id, current_timer_id, winner_can_exit
    waiting_for_next = True
    winner_can_exit = False
    if current_timer_id:
        stateVars.root.after_cancel(current_timer_id)
        current_timer_id = None

    titleLabel.place_forget()
    quizPlayerLabel.place_forget()
    quizTimerLabel.place_forget()
    quizStatusLabel.place_forget()
    quizPauseButton.place_forget()
    quizQuitButton.place_forget()

    quizQuestionLabel.config(text=f"WINNER:\n{winner_name}", fg="#FFD700", font=winnerFont)
    quizQuestionLabel.place(x=(rootWidth // 2), y=(rootHeight // 2) - 80, anchor="center")

    winner_flashing = True
    flash_winner_colors()
    stateVars.root.bind("<Key>", handle_winner_keypress)
    stateVars.root.after(7000, lambda: globals().update(winner_can_exit=True))

def flash_winner_colors():
    global winner_timer_id, winner_flashing
    if not winner_flashing:
        return
    current_bg = stateVars.root.cget("bg")
    comp_color = "#001133"
    next_bg = comp_color if current_bg == background_colour else background_colour
    stateVars.root.configure(bg=next_bg)
    stateVars.crt_canvas.configure(bg=next_bg)
    quizQuestionLabel.config(bg=next_bg)
    winner_timer_id = stateVars.root.after(250, flash_winner_colors)

def handle_winner_keypress(event):
    global winner_flashing, winner_timer_id, winner_can_exit
    if not winner_can_exit or event.char.lower() != 'n':
        return "break"
    if winner_timer_id:
        stateVars.root.after_cancel(winner_timer_id)
        winner_timer_id = None
    winner_flashing = False
    stateVars.root.unbind("<Key>")
    stateVars.root.configure(bg=background_colour)
    stateVars.crt_canvas.configure(bg=background_colour)
    quizQuestionLabel.config(bg=background_colour, fg=foreground_colour, font=descFont)
    quizQuestionLabel.place_forget()
    titleLabel.place(x=(rootWidth // 2), y=20, anchor="n")
    pygame.mixer.music.set_volume(0.3)
    stateVars.crt_canvas.itemconfigure("scanlines", state="normal")
    stateVars.crt_canvas.itemconfigure(moving_scanline, state="normal")
    show_terminal_from_quiz()
    print_term("Quiz finished and winner crowned. \n")
    return "break"

def end_quiz(msg):
    global current_timer_id
    if current_timer_id:
        stateVars.root.after_cancel(current_timer_id)
        current_timer_id = None
    stateVars.root.unbind("<Key>")
    quizPlayerLabel.place_forget()
    quizQuestionLabel.place_forget()
    quizTimerLabel.place_forget()
    quizStatusLabel.place_forget()
    quizPauseButton.place_forget()
    quizQuitButton.place_forget()
    titleLabel.place(x=(rootWidth // 2), y=20, anchor="n")
    pygame.mixer.music.set_volume(0.3)
    stateVars.crt_canvas.itemconfigure("scanlines", state="normal")
    stateVars.crt_canvas.itemconfigure(moving_scanline, state="normal")
    show_terminal_from_quiz()
    print_term(msg)

def execute_command(e=None):
    global quiz_setup_step
    raw_cmd = termEntry.get().strip().lower()
    termEntry.delete(0, "end")

    if quiz_setup_step > 0:
        termText.config(state="normal")
        termText.insert("end", f"{raw_cmd}\n")
        termText.config(state="disabled")
        handle_quiz_setup_input(raw_cmd)
        return

    termText.config(state="normal")
    termText.insert("end", f"{raw_cmd}")
    termText.config(state="disabled")

    sub_commands = [c.strip() for c in raw_cmd.split("&&") if c.strip()]

    commands = {
        "help": lambda: print_term("Commands: quiz, syntax, rickroll, suggest, bug, luck, clear, about, exit, cls \n"),
        "quiz": lambda: (print_term("Available commands: player, question, start, preface, keys, about \nCommands for this must start with 'quiz '\n"), termEntry.insert(tk.END, "quiz ")),
        "quiz preface": lambda: preface_quiz(),
        "quiz keys": lambda: print_term("Quiz Key Bindings during gameplay:\n- 'y': Correct answer (stays in, press 'n' for next)\n- 'i': Incorrect answer (eliminated, press 'n' for next)\n- 'p': Skip question (stays in, press 'n' for next)\n- 'q': Trigger last chance manually (sets skips to 0, adds 5s to timer)\n- 'n': Proceed to next turn after a screen flash\n"),
        "quiz about": lambda: print_term("Quiz Usage & Purpose:\nDesigned to be operated by a host standing in front of a class or participating audience. The host listens out for player responses in the room and inputs the corresponding key commands into the CRT interface. \nYou cn type 'quiz keys' to see what the keybinds are for moving questions along! \n"),
        "quiz start": lambda: start_quiz_setup(),
        "quiz player": lambda: (print_term("Available commands: load, lookup, default \nCommands for this must start with 'quiz player '\n"), termEntry.insert(tk.END, "quiz player ")),
        "quiz question": lambda: (print_term("Available commands: load, lookup, default \nCommands for this must start with 'quiz question '\n"), termEntry.insert(tk.END, "quiz question ")),
        "quiz player load": lambda: (print_term("Loading playerlist.txt \n"), load_playerlist()),
        "quiz question load": lambda: (print_term("Loading questionlist.txt \n"), load_questionlist()),
        "quiz player lookup": lambda: (show_playerlist()),
        "quiz question lookup": lambda: (show_questionlist()),
        "quiz player default": lambda: load_default_players(),
        "quiz question default": lambda: load_default_questions(),
        "suggest": lambda: (print_term("Opening GitHub issue template for feature suggestion...\n"), webbrowser.open_new("https://github.com/sadgituser/CRT-MultiApp/issues/new?template=bug_report.md")),
        "bug": lambda: (print_term("Opening GitHub issue template for bug report...\n"), webbrowser.open_new("https://github.com/sadgituser/CRT-MultiApp/issues/new?template=suggest_feature.md")),
        "syntax": lambda: (show_syntax()),
        "rickroll": lambda: (print_term("RICKROLL!\n"), webbrowser.open_new("https://www.youtube.com/watch?v=a7Lq6ZlSqys")),
        "luck": lambda: (print_term("Opening Lucky Gamble... \n"), testLuck()),
        "clear": lambda: (clear_term(), stateVars.root.after(100, termText.insert("end", "CRT OS v1.0\nType 'help' for commands. \n\n> "))),
        "cls": lambda: (clear_term(), stateVars.root.after(100, termText.insert("end", "CRT OS v1.0\nType 'help' for commands. \n\n> "))),
        "about": lambda: (print_term("Terra (Hackclub) CRT App! Check out the GitHub for more info! \n"), openMePages()),
        "exit": stateVars.root.destroy
    }

    for cmd in sub_commands:
        if cmd in commands:
            commands[cmd]()
        else:
            print_term(f"Unknown command: '{cmd}'. Type 'help' for a list of commands! \n")
            break


# Music Logic
try:
    pygame.mixer.music.load(bg_music_path)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except Exception as e:
    messagebox.showerror("Music Fail", f"Failed to load background music: {str(e)}")


# Initialise main window
apply_crt_flicker()
termEntry.bind("<Return>", execute_command)
stateVars.root.mainloop()
