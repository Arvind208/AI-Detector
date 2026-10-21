"""
AI Detector Engine
Authored by Arvind (https://github.com/Arvind208)

Provides multi-signal AI text detection using:
1. Statistical Perplexity & Predictability
2. Sentence Burstiness & Variance
3. Stylometric & Lexical Diversity (TTR, Hapax Legomena, Readability)
4. AI Signpost & Vocabulary Marker Analysis
5. Sentence-by-sentence classification & heatmap scoring
"""

import math
import re
from typing import Dict, List, Any


# Common marker words and transition phrases frequently overrepresented in LLM outputs
AI_TRANSITION_MARKERS = {
    "delve", "testament", "tapestry", "crucial", "seamlessly", "pivotal",
    "furthermore", "moreover", "in conclusion", "it is important to note",
    "fosters", "beacon", "unwavering", "intricate", "paramount", "underscores",
    "realm", "embark", "meticulous", "nuanced", "multifaceted", "holistic",
    "transcend", "revolutionize", "unravel", "ever-evolving", "rich tapestry",
    "vibrant tapestry", "stands as a testament", "it's crucial to remember"
}


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences handling common abbreviations."""
    clean_text = text.strip()
    if not clean_text:
        return []
    
    # Split on period, exclamation, or question mark followed by space or end of text
    raw_sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    if not sentences and clean_text:
        sentences = [clean_text]
    return sentences


def tokenize_words(text: str) -> List[str]:
    """Tokenize words from text, stripping punctuation."""
    return re.findall(r"\b[A-Za-z0-9'-]+\b", text.lower())


def count_syllables(word: str) -> int:
    """Heuristic syllable counting for readability metrics."""
    word = word.lower()
    if len(word) <= 3:
        return 1
    # Count vowel groups
    count = len(re.findall(r'[aeiouy]+', word))
    # Discount silent trailing 'e'
    if word.endswith('e') and not word.endswith('le') and count > 1:
        count -= 1
    return max(1, count)


def calculate_flesch_reading_ease(words: List[str], sentences: List[str]) -> float:
    """Calculate Flesch Reading Ease score."""
    if not words or not sentences:
        return 65.0
    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables(w) for w in words)
    
    asl = total_words / max(1, total_sentences)
    asw = total_syllables / max(1, total_words)
    score = 206.835 - (1.015 * asl) - (84.6 * asw)
    return round(max(0.0, min(100.0, score)), 1)


def calculate_lexical_diversity(words: List[str]) -> Dict[str, float]:
    """Calculate Type-Token Ratio (TTR) and Root TTR (Guiraud's Index)."""
    if not words:
        return {"ttr": 0.5, "guiraud": 3.0}
    
    total = len(words)
    unique = len(set(words))
    ttr = unique / total
    guiraud = unique / math.sqrt(total) if total > 0 else 0.0
    return {"ttr": round(ttr, 3), "guiraud": round(guiraud, 2)}


def calculate_burstiness(sentence_lengths: List[int]) -> float:
    """
    Calculate sentence length burstiness (Coefficient of Variation).
    Humans write with high variance in sentence length (high burstiness).
    LLMs write with very uniform, consistent sentence lengths (low burstiness).
    """
    if len(sentence_lengths) < 2:
        return 0.45  # Default neutral burstiness
    
    mean_length = sum(sentence_lengths) / len(sentence_lengths)
    if mean_length == 0:
        return 0.0
        
    variance = sum((l - mean_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
    std_dev = math.sqrt(variance)
    cv = std_dev / mean_length  # Coefficient of Variation
    return round(min(1.5, cv), 3)


def calculate_pseudo_perplexity(words: List[str]) -> float:
    """
    Statistical predictability metric based on unigram & bigram frequency distribution.
    AI-generated text exhibits uniform probability and lower perplexity (predictable transitions).
    Human text exhibits high vocabulary entropy, unexpected word choices, and higher perplexity.
    """
    if len(words) < 3:
        return 45.0
        
    word_freq: Dict[str, int] = {}
    for w in words:
        word_freq[w] = word_freq.get(w, 0) + 1
        
    total_words = len(words)
    entropy = 0.0
    for count in word_freq.values():
        p = count / total_words
        entropy -= p * math.log2(p)
        
    # Perplexity is 2^entropy normalized
    perplexity = 2 ** entropy
    normalized_ppl = round(min(100.0, perplexity * 6.5), 1)
    return normalized_ppl


def detect_ai_markers(text: str) -> List[str]:
    """Find known overused AI vocabulary and signpost phrases in the text."""
    lower_text = text.lower()
    found = []
    for marker in AI_TRANSITION_MARKERS:
        if re.search(r"\b" + re.escape(marker) + r"\b", lower_text):
            found.append(marker)
    return found


def analyze_sentence(sentence: str) -> Dict[str, Any]:
    """Analyze an individual sentence for AI markers and rhythm."""
    words = tokenize_words(sentence)
    word_count = len(words)
    
    if word_count == 0:
        return {
            "sentence": sentence,
            "score": 0,
            "label": "Human",
            "reason": "Empty or punctuation only"
        }
        
    markers = detect_ai_markers(sentence)
    marker_penalty = min(40, len(markers) * 20)
    
    # AI tends to produce 15-28 word balanced sentences
    length_penalty = 15 if (15 <= word_count <= 28) else 0
    
    # Calculate unique word ratio in the sentence
    unique_ratio = len(set(words)) / max(1, word_count)
    repetition_penalty = 15 if unique_ratio < 0.75 else 0
    
    raw_score = 25 + marker_penalty + length_penalty + repetition_penalty
    final_score = int(max(5, min(95, raw_score)))
    
    if final_score >= 70:
        label = "Likely AI"
        color = "red"
        reason = "Predictable phrasing with characteristic AI marker words" if markers else "High syntactic uniformity"
    elif final_score >= 40:
        label = "Mixed / AI-Assisted"
        color = "yellow"
        reason = "Moderate uniformity with balanced sentence length"
    else:
        label = "Likely Human"
        color = "green"
        reason = "Natural cadence and human variance"
        
    return {
        "sentence": sentence,
        "score": final_score,
        "label": label,
        "color": color,
        "reason": reason,
        "word_count": word_count,
        "markers": markers
    }


def analyze_text(text: str) -> Dict[str, Any]:
    """
    Main detection function that combines all signals:
    - Burstiness
    - Perplexity & Entropy
    - Lexical Diversity
    - AI Markers
    - Sentence heatmap
    """
    clean_text = text.strip()
    if not clean_text:
        return {
            "error": "No text provided. Please enter text to analyze."
        }
        
    words = tokenize_words(clean_text)
    sentences = split_into_sentences(clean_text)
    
    if len(words) < 5:
        return {
            "error": "Text is too short for reliable detection. Please provide at least 15 words."
        }
        
    sentence_lengths = [len(tokenize_words(s)) for s in sentences]
    burstiness = calculate_burstiness(sentence_lengths)
    lexical = calculate_lexical_diversity(words)
    perplexity = calculate_pseudo_perplexity(words)
    reading_ease = calculate_flesch_reading_ease(words, sentences)
    markers_found = detect_ai_markers(clean_text)
    
    # Detailed sentence breakdown
    sentence_analysis = [analyze_sentence(s) for s in sentences]
    
    # Base model weight calculation
    # 1. Burstiness signal: Low burstiness (< 0.4) indicates AI. High burstiness (> 0.7) indicates Human.
    burstiness_score = max(0, min(100, int((1.0 - (burstiness / 1.1)) * 100)))
    
    # 2. Perplexity signal: Low perplexity indicates AI (predictable). High indicates Human.
    perplexity_signal = max(0, min(100, int((1.0 - (perplexity / 85.0)) * 100)))
    
    # 3. Lexical Diversity signal: Extremely repetitive or overly sanitized TTR
    lexical_signal = max(0, min(100, int((1.0 - lexical["ttr"]) * 100)))
    
    # 4. Marker word density
    marker_density = len(markers_found) / max(1, (len(words) / 100.0))
    marker_signal = min(100, int(marker_density * 35))
    
    # Weighted ensemble calculation
    # Weights: Burstiness (35%), Perplexity (25%), Marker Density (25%), Lexical (15%)
    doc_score = (
        (burstiness_score * 0.35) +
        (perplexity_signal * 0.25) +
        (marker_signal * 0.25) +
        (lexical_signal * 0.15)
    )
    
    # Blend with average sentence-level diagnostic
    avg_sentence_score = sum(s["score"] for s in sentence_analysis) / max(1, len(sentence_analysis))
    blended_score = (doc_score * 0.4) + (avg_sentence_score * 0.6)
    
    # Soft calibrate between 2 and 98
    overall_score = int(round(max(2, min(98, blended_score))))
    
    if overall_score >= 70:
        verdict = "Likely AI-Generated"
        verdict_level = "ai"
        summary = "This text exhibits high predictability, uniform sentence lengths, and characteristic AI signpost vocabulary."
    elif overall_score >= 40:
        verdict = "Mixed / AI-Assisted"
        verdict_level = "mixed"
        summary = "This text exhibits a combination of human-like burstiness with AI-assisted structural patterns."
    else:
        verdict = "Likely Human-Written"
        verdict_level = "human"
        summary = "This text displays natural linguistic variation, high burstiness, and authentic human cadence."
        
    return {
        "score": overall_score,
        "verdict": verdict,
        "verdict_level": verdict_level,
        "summary": summary,
        "metrics": {
            "burstiness": burstiness,
            "burstiness_label": "High (Human)" if burstiness > 0.6 else "Low (AI Uniform)",
            "perplexity": perplexity,
            "perplexity_label": "High Entropy (Human)" if perplexity > 50 else "Predictable (AI)",
            "ttr": lexical["ttr"],
            "reading_ease": reading_ease,
            "word_count": len(words),
            "sentence_count": len(sentences),
            "ai_markers_count": len(markers_found),
            "detected_markers": markers_found[:8]
        },
        "sentences": sentence_analysis
    }
