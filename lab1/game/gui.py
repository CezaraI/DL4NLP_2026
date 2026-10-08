"""Tkinter interface for the Word Association Game.

Run with:  python gui.py
Requires game.py and wordnet_relations.py in the same folder.
"""

import random
import tkinter as tk
from tkinter import messagebox, ttk

from game import (
    RELATION_BONUS,
    RELATION_NAMES,
    ROUNDS,
    TARGETS,
    TRIES,
    closeness,
    find_relation,
    similarity,
)
from wordnet_relations import related_words

RULES = (
    f"- You play {ROUNDS} rounds with {TRIES} guesses each.\n"
    "- Type English words related to the word shown.\n"
    "- The closer a word is semantically, the more points it earns (up to 70).\n"
    f"- A direct WordNet relation (synonym, antonym, hypernym, hyponym, meronym) "
    f"adds a bonus of {RELATION_BONUS} points.\n"
    "- Use 'Skip round' to end a round early."
)


def color_for(sim):
    """Color used for the closeness label and the guess log."""
    if sim >= 0.85:
        return "#1b8a3a"
    if sim >= 0.65:
        return "#5a9e2c"
    if sim >= 0.45:
        return "#c99700"
    if sim >= 0.25:
        return "#d9650b"
    return "#777777"


class GameApp:
    def __init__(self, root):
        self.root = root
        root.title("Word Association Game")
        root.geometry("640x640")
        root.minsize(560, 560)

        self._build_ui()
        self.new_game()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=(16, 12, 16, 0))
        top.pack(fill="x")
        self.round_label = ttk.Label(top, font=("Helvetica", 11))
        self.round_label.pack(side="left")
        self.score_label = ttk.Label(top, font=("Helvetica", 11, "bold"))
        self.score_label.pack(side="right")

        self.target_label = ttk.Label(
            self.root, font=("Helvetica", 32, "bold"), anchor="center"
        )
        self.target_label.pack(fill="x", pady=(10, 0))

        self.definition_label = ttk.Label(
            self.root, wraplength=580, justify="center", foreground="#555555"
        )
        self.definition_label.pack(padx=20, pady=(2, 10))

        entry_row = ttk.Frame(self.root, padding=(16, 0))
        entry_row.pack(fill="x")
        self.entry = ttk.Entry(entry_row, font=("Helvetica", 14))
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.submit)
        self.submit_button = ttk.Button(entry_row, text="Guess", command=self.submit)
        self.submit_button.pack(side="left", padx=(8, 0))

        self.attempts_label = ttk.Label(self.root, foreground="#555555")
        self.attempts_label.pack(pady=(6, 0))

        self.message_label = ttk.Label(self.root, foreground="#b00020")
        self.message_label.pack()

        meter = ttk.Frame(self.root, padding=(16, 4))
        meter.pack(fill="x")
        self.closeness_label = ttk.Label(
            meter, text="Closeness: -", font=("Helvetica", 12, "bold")
        )
        self.closeness_label.pack(anchor="w")
        self.meter = ttk.Progressbar(meter, maximum=100, length=300)
        self.meter.pack(fill="x", pady=(2, 0))

        log_frame = ttk.Frame(self.root, padding=(16, 8))
        log_frame.pack(fill="both", expand=True)
        self.log_box = tk.Text(
            log_frame, height=10, wrap="word", state="disabled",
            font=("Helvetica", 11), relief="flat", background="#f6f6f6",
        )
        scroll = ttk.Scrollbar(log_frame, command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log_box.pack(side="left", fill="both", expand=True)
        self.log_box.tag_configure("bold", font=("Helvetica", 11, "bold"))
        self.log_box.tag_configure("dim", foreground="#666666")

        buttons = ttk.Frame(self.root, padding=(16, 0, 16, 12))
        buttons.pack(fill="x")
        self.action_button = ttk.Button(buttons, command=self.action)
        self.action_button.pack(side="left")
        ttk.Button(buttons, text="Rules", command=self.show_rules).pack(side="right")
        ttk.Button(buttons, text="New game", command=self.new_game).pack(
            side="right", padx=(0, 8)
        )

    def log(self, text, tag=None, color=None):
        self.log_box.configure(state="normal")
        if color:
            self.log_box.tag_configure(color, foreground=color)
            tag = (tag, color) if tag else color
        self.log_box.insert("end", text, tag)
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def show_rules(self):
        messagebox.showinfo("Rules", RULES)

    def refresh_header(self):
        self.round_label.config(text=f"Round {self.round_no}/{ROUNDS}")
        self.score_label.config(text=f"Total score: {self.total + self.score}")
        left = TRIES - self.attempts
        self.attempts_label.config(text=f"Guesses left: {left}")

    # ---------------------------------------------------------------- game

    def new_game(self):
        self.targets = random.sample(TARGETS, ROUNDS)
        self.round_no = 0
        self.total = 0
        self.score = 0
        self.attempts = 0
        self.start_round()

    def start_round(self):
        self.round_no += 1
        self.target = self.targets[self.round_no - 1]
        self.relations = related_words(self.target)
        self.relations["synonyms"] = [
            w for w in self.relations["synonyms"] if w != self.target
        ]
        definition = self.relations["definitions"][0].split(": ", 1)[1]

        self.guessed = set()
        self.score = 0
        self.attempts = 0
        self.round_over = False

        self.target_label.config(text=self.target.upper())
        self.definition_label.config(text=definition)
        self.message_label.config(text="")
        self.closeness_label.config(text="Closeness: -", foreground="black")
        self.meter["value"] = 0
        self.clear_log()
        self.log("Type a word related to the target above and press Enter.\n", "dim")
        self.action_button.config(text="Skip round")
        self.entry.config(state="normal")
        self.submit_button.config(state="normal")
        self.entry.delete(0, "end")
        self.entry.focus_set()
        self.refresh_header()

    def submit(self, event=None):
        if self.round_over:
            return
        guess = self.entry.get().strip().lower()
        self.entry.delete(0, "end")
        if not guess:
            return

        error = self.validate(guess)
        if error:
            self.message_label.config(text=error)
            return
        self.message_label.config(text="")

        self.guessed.add(guess)
        self.attempts += 1

        sim = similarity(self.target, guess)
        relation = find_relation(guess, self.relations)
        points = round(sim * 70) + (RELATION_BONUS if relation else 0)
        self.score += points

        color = color_for(sim)
        self.closeness_label.config(
            text=f"Closeness: {closeness(sim)} ({sim:.2f})", foreground=color
        )
        self.meter["value"] = sim * 100

        self.log(f"{guess}", "bold", color)
        self.log(f"   +{points} points   {closeness(sim)} (similarity {sim:.2f})\n")
        if relation:
            self.log(f"   '{guess}' is {relation} of '{self.target}'\n", "dim")

        self.refresh_header()
        if self.attempts >= TRIES:
            self.end_round()

    def validate(self, guess):
        from nltk.corpus import wordnet as wn

        if guess == self.target:
            return "That is the target word, try something else."
        if guess in self.guessed:
            return "You already tried that word."
        if not wn.synsets(guess.replace(" ", "_")):
            return f"'{guess}' is not in WordNet."
        return None

    def end_round(self):
        self.round_over = True
        self.total += self.score
        self.score = 0
        self.entry.config(state="disabled")
        self.submit_button.config(state="disabled")

        self.log(f"\nRound finished. Total so far: {self.total}\n", "bold")
        self.log("Words you could have tried:\n", "dim")
        for key, name in RELATION_NAMES.items():
            missed = [w for w in self.relations[key] if w not in self.guessed]
            if missed:
                sample = random.sample(missed, min(3, len(missed)))
                self.log(f"  {key}: {', '.join(sample)}\n")

        self.refresh_header()
        if self.round_no == ROUNDS:
            self.action_button.config(text="Play again")
            messagebox.showinfo("Game over", f"Final score: {self.total} points")
        else:
            self.action_button.config(text="Next round")

    def action(self):
        if not self.round_over:
            self.end_round()
        elif self.round_no == ROUNDS:
            self.new_game()
        else:
            self.start_round()


def main():
    root = tk.Tk()
    try:
        related_words("dog")  # makes sure WordNet is installed
    except RuntimeError as error:
        messagebox.showerror("WordNet missing", str(error))
        return
    GameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()