# WordNet Relations

This project is the Python-file version of `Tema 1 nlp.ipynb`. It looks up a word in NLTK WordNet and prints its synonyms, hypernyms, hyponyms, antonyms, meronyms, and definitions.

## Setup

From this directory, install the Python dependency:

```powershell
python -m pip install -r requirements.txt
```

Download the WordNet corpora once:

```powershell
python main.py --download-data
```

## Run

Run interactively and enter a word when prompted:

```powershell
python main.py
```

Or provide a word directly:

```powershell
python main.py dog
python main.py "ice cream"
```

## Files

- `wordnet_relations.py` contains the reusable WordNet functions.
- `main.py` contains the command-line argument handling and program entry point.
- `requirements.txt` lists the Python dependency.
- `Tema 1 nlp.ipynb` is the original notebook.
