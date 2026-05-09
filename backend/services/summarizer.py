from transformers import pipeline

_summarizer = None
_summarizer_init_error = None


def generate_summary(text: str, max_chars: int = 600) -> str:
    """
    Fast heuristic-based summarization to prevent timeouts during batch uploads.
    Extracts the most significant sentences from the beginning.
    """
    if not text or not text.strip():
        return "No text available for summarization."

    # Remove excessive whitespace
    clean_text = " ".join(text.split())

    # Try to find the abstract or introduction first
    import re
    abstract_match = re.search(r"(?:abstract|summary|introduction)[:\s]*(.*?)(?:\n\s*\n|1\. Introduction|2\. )", clean_text, re.IGNORECASE | re.DOTALL)

    if abstract_match:
        summary = abstract_match.group(1).strip()
    else:
        # Fallback: Just take the first few hundred characters
        summary = clean_text

    if len(summary) > max_chars:
        return f"{summary[:max_chars].rstrip()}..."

    return summary if len(summary) > 50 else f"{clean_text[:max_chars]}..."