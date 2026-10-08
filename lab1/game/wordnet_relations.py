import nltk
from nltk.corpus import wordnet as wn


def download_wordnet_data():
    """Download the WordNet data used by the program."""
    nltk.download("wordnet")
    nltk.download("omw-1.4")


def check_wordnet():
    """Check whether the WordNet data is available."""
    try:
        wn.ensure_loaded()
    except LookupError as error:
        raise RuntimeError(
            "WordNet data is not installed. Run "
            "`python main.py --download-data` and try again."
        ) from error


def related_words(word: str) -> dict:
    """Find WordNet relations for all senses of a word."""
    check_wordnet()

    # WordNet folosește caracterul _ pentru expresiile formate din mai multe cuvinte.
    word = word.strip().lower().replace(" ", "_")
    synsets = wn.synsets(word)

    synonyms = set()
    hypernyms = set()
    hyponyms = set()
    antonyms = set()
    meronyms = set()
    definitions = set()

    for synset in synsets:
        definitions.add(f"{synset.name()}: {synset.definition()}")

        # Lemele unui synset reprezintă sinonimele lui.
        for lemma in synset.lemmas():
            synonyms.add(lemma.name().replace("_", " "))

            # Unele sinonime au și antonime salvate în WordNet.
            for antonym in lemma.antonyms():
                antonyms.add(antonym.name().replace("_", " "))

        # Hypernym = un concept mai general.
        for hypernym in synset.hypernyms():
            for lemma in hypernym.lemmas():
                hypernyms.add(lemma.name().replace("_", " "))

        # Hyponym = un concept mai specific.
        for hyponym in synset.hyponyms():
            for lemma in hyponym.lemmas():
                hyponyms.add(lemma.name().replace("_", " "))

        # Meronimele sunt părți, membri sau substanțe ale conceptului.
        meronym_relations = (
            synset.part_meronyms()
            + synset.member_meronyms()
            + synset.substance_meronyms()
        )
        for meronym in meronym_relations:
            for lemma in meronym.lemmas():
                meronyms.add(lemma.name().replace("_", " "))

    # Seturile elimină duplicatele, iar sorted() face afișarea ordonată.
    return {
        "synonyms": sorted(synonyms),
        "hypernyms": sorted(hypernyms),
        "hyponyms": sorted(hyponyms),
        "antonyms": sorted(antonyms),
        "meronyms": sorted(meronyms),
        "definitions": sorted(definitions),
    }


def print_relations(relations: dict):
    """Print the results in an easy-to-read format."""
    for relation, words in relations.items():
        print(f"\n{relation.capitalize()}:")
        if words:
            for word in words:
                print(f"  - {word}")
        else:
            print("  None")
