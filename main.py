import argparse

from wordnet_relations import (
    download_wordnet_data,
    print_relations,
    related_words,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Display WordNet relations for a word."
    )
    parser.add_argument(
        "word",
        nargs="?",
        help="the word to look up; if missing, it will be requested interactively",
    )
    parser.add_argument(
        "--download-data",
        action="store_true",
        help="download the WordNet data",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.download_data:
        download_wordnet_data()
        print("WordNet data downloaded successfully.")
        raise SystemExit

    # Dacă nu am primit cuvântul în comandă, îl citim de la tastatură.
    word = args.word
    if word is None:
        word = input("Enter a word: ")

    word = word.strip().lower()

    if not word:
        print("Please enter a word.")
        raise SystemExit

    try:
        relations = related_words(word)
    except RuntimeError as error:
        print(error)
        raise SystemExit(1) from error

    if not relations["definitions"]:
        print(f"No WordNet entries found for '{word}'.")
        raise SystemExit

    print_relations(relations)
