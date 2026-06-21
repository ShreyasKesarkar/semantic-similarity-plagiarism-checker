"""
setup_nltk.py
-------------
Run this once after installing requirements.txt / installing this
package, to download the NLTK sentence tokenizer data needed by
document_preprocessor/segmenter.py.

    python scripts/setup_nltk.py
"""

import nltk

if __name__ == "__main__":
    print("Downloading NLTK 'punkt_tab' tokenizer data...")
    nltk.download("punkt_tab")
    print("Done.")
