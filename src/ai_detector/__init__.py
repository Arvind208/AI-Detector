"""
AI Sentinel - AI Text Detection Engine
Authored by Arvind (https://github.com/Arvind208)
"""

from .engine import analyze_text, analyze_sentence, split_into_sentences, tokenize_words

__version__ = "1.0.0"
__author__ = "Arvind (https://github.com/Arvind208)"

__all__ = [
    "analyze_text",
    "analyze_sentence",
    "split_into_sentences",
    "tokenize_words",
]
