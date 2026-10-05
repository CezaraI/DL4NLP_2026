"""Reusable WordNet relation functions.

Install the Python dependency with ``python -m pip install -r requirements.txt``
and download the WordNet data before calling :func:`related_words`.
"""

from __future__ import annotations

from typing import TypedDict

import nltk
from nltk.corpus import wordnet as wn


class WordNetRelations(TypedDict):
    """The relation categories returned for a word."""

    synonyms: list[str]
    hypernyms: list[str]
    hyponyms: list[str]
    antonyms: list[str]
    meronyms: list[str]
    definitions: list[str]


def download_wordnet_data() -> None:
    """Download the WordNet corpora used by this project."""

    nltk.download("wordnet")
    nltk.download("omw-1.4")


def _load_wordnet() -> None:
    """Ensure WordNet is available and provide a useful setup error."""

    try:
        wn.ensure_loaded()
    except LookupError as error:
        raise RuntimeError(
            "WordNet data is not installed. Run "
            "`python main.py --download-data` and try again."
        ) from error


def _normalise_lemma(name: str) -> str:
    """Convert WordNet lemma names into readable text."""

    return name.replace("_", " ")


def related_words(word: str) -> WordNetRelations:
    """Return direct WordNet relations and definitions for ``word``.

    The function combines all WordNet senses for the word. Hypernyms,
    hyponyms, and meronyms are direct one-level relations, matching the
    original notebook implementation.
    """

    _load_wordnet()

    result: WordNetRelations = {
        "synonyms": [],
        "hypernyms": [],
        "hyponyms": [],
        "antonyms": [],
        "meronyms": [],
        "definitions": [],
    }

    # WordNet uses underscores for multiword lemmas.
    lookup_word = word.strip().lower().replace(" ", "_")
    synsets = wn.synsets(lookup_word)

    synonyms: set[str] = set()
    hypernyms: set[str] = set()
    hyponyms: set[str] = set()
    antonyms: set[str] = set()
    meronyms: set[str] = set()
    definitions: set[str] = set()

    for synset in synsets:
        definitions.add(f"{synset.name()}: {synset.definition()}")

        for lemma in synset.lemmas():
            synonyms.add(_normalise_lemma(lemma.name()))
            antonyms.update(
                _normalise_lemma(antonym.name())
                for antonym in lemma.antonyms()
            )

        for hypernym in synset.hypernyms():
            hypernyms.update(
                _normalise_lemma(lemma.name())
                for lemma in hypernym.lemmas()
            )

        for hyponym in synset.hyponyms():
            hyponyms.update(
                _normalise_lemma(lemma.name())
                for lemma in hyponym.lemmas()
            )

        meronym_relations = (
            synset.part_meronyms()
            + synset.member_meronyms()
            + synset.substance_meronyms()
        )
        for meronym in meronym_relations:
            meronyms.update(
                _normalise_lemma(lemma.name())
                for lemma in meronym.lemmas()
            )

    return {
        "synonyms": sorted(synonyms),
        "hypernyms": sorted(hypernyms),
        "hyponyms": sorted(hyponyms),
        "antonyms": sorted(antonyms),
        "meronyms": sorted(meronyms),
        "definitions": sorted(definitions),
    }


def print_relations(relations: WordNetRelations) -> None:
    """Print relation results in the same readable format as the notebook."""

    for relation, words in relations.items():
        print(f"\n{relation.capitalize()}:")
        if words:
            for item in words:
                print(f"  - {item}")
        else:
            print("  None")
