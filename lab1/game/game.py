"""Word Association Game - uses the relations from wordnet_relations.py."""

import random

from nltk.corpus import wordnet as wn

from wordnet_relations import related_words

TARGETS = [
    "dog", "car", "tree", "house", "doctor", "computer", "book", "river",
    "bird", "music", "school", "mountain", "flower", "bread", "ocean",
    "teacher", "airplane", "chair", "hand", "garden", "clock", "bridge",
]

ROUNDS = 5
TRIES = 5
RELATION_BONUS = 30  # extra points for a direct WordNet relation

RELATION_NAMES = {
    "synonyms": "a synonym",
    "antonyms": "an antonym",
    "hypernyms": "a hypernym (more general term)",
    "hyponyms": "a hyponym (more specific term)",
    "meronyms": "a meronym (part of it)",
}


def similarity(word1, word2):
    """Highest Wu-Palmer similarity over all sense pairs with the same part of speech."""
    best = 0.0
    for a in wn.synsets(word1.replace(" ", "_")):
        for b in wn.synsets(word2.replace(" ", "_")):
            if a.pos() == b.pos():
                score = a.wup_similarity(b)
                if score and score > best:
                    best = score
    return best


def find_relation(guess, relations):
    """Return the direct relation between guess and the target, or None."""
    for key, name in RELATION_NAMES.items():
        if guess in relations[key]:
            return name
    return None


def closeness(sim):
    if sim >= 0.85:
        return "Very close!"
    if sim >= 0.65:
        return "Close"
    if sim >= 0.45:
        return "Warm"
    if sim >= 0.25:
        return "Far"
    return "Unrelated"


def play_round(target, number):
    relations = related_words(target)
    relations["synonyms"] = [w for w in relations["synonyms"] if w != target]

    definition = relations["definitions"][0].split(": ", 1)[1]
    print(f"\n=== Round {number}/{ROUNDS} ===")
    print(f"Word: {target.upper()}  ({definition})")

    guessed = set()
    score = 0
    attempts = 0

    while attempts < TRIES:
        guess = input(f"[{attempts + 1}/{TRIES}] Your word (or 'skip'/'quit'): ")
        guess = guess.strip().lower()

        if guess == "quit":
            return score, True
        if guess == "skip":
            break
        if not guess:
            continue
        if guess == target:
            print("That is the target word, try something else.")
            continue
        if guess in guessed:
            print("You already tried that word.")
            continue
        if not wn.synsets(guess.replace(" ", "_")):
            print(f"'{guess}' is not in WordNet.")
            continue

        guessed.add(guess)
        attempts += 1

        sim = similarity(target, guess)
        relation = find_relation(guess, relations)
        points = round(sim * 70) + (RELATION_BONUS if relation else 0)
        score += points

        print(f"  Closeness: {closeness(sim)} (similarity {sim:.2f})")
        if relation:
            print(f"  Relation:  '{guess}' is {relation} of '{target}'")
        print(f"  Points:    +{points} (round total: {score})")

    print(f"\nRound score: {score}")
    print("Words you could have tried:")
    for key, name in RELATION_NAMES.items():
        missed = [w for w in relations[key] if w not in guessed]
        if missed:
            sample = random.sample(missed, min(3, len(missed)))
            print(f"  {key}: {', '.join(sample)}")
    return score, False


def main():
    print("WORD ASSOCIATION GAME")
    print("Rules:")
    print(f"  - You play {ROUNDS} rounds with {TRIES} guesses each.")
    print("  - Type English words related to the word shown.")
    print("  - The closer a word is semantically, the more points it earns (up to 70).")
    print(f"  - A direct WordNet relation (synonym, antonym, hypernym, hyponym,")
    print(f"    meronym) adds a bonus of {RELATION_BONUS} points.")
    print("  - Type 'skip' to end a round early or 'quit' to stop the game.")

    total = 0
    for number, target in enumerate(random.sample(TARGETS, ROUNDS), start=1):
        score, quit_game = play_round(target, number)
        total += score
        if quit_game:
            break

    print(f"\nFinal score: {total} points")


if __name__ == "__main__":
    main()