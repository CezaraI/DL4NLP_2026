"""Command-line entry point for the WordNet relations program."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from wordnet_relations import (
    WordNetRelations,
    download_wordnet_data,
    print_relations,
    related_words,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line options."""

    parser = argparse.ArgumentParser(
        description="Display WordNet relations for a word."
    )
    parser.add_argument(
        "word",
        nargs="?",
        help="word to look up; if omitted, you will be prompted",
    )
    parser.add_argument(
        "--download-data",
        action="store_true",
        help="download the NLTK WordNet corpora and exit",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the interactive or command-line WordNet program."""

    args = parse_args(argv)

    if args.download_data:
        download_wordnet_data()
        print("WordNet data downloaded successfully.")
        return 0

    word = args.word
    if word is None:
        word = input("Enter a word: ")

    word = word.strip().lower()
    if not word:
        print("Please enter a word.")
        return 0

    try:
        relations: WordNetRelations = related_words(word)
    except RuntimeError as error:
        print(error)
        return 1

    if not relations["definitions"]:
        print(f"No WordNet entries found for '{word}'.")
        return 0

    print_relations(relations)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
