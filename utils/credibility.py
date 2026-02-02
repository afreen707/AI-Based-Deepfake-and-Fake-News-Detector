def compute_credibility(text_score, media_score=None):
    """
    Combines text and media scores into a final credibility score
    """
    if media_score is None:
        # Only text available
        final_score = text_score
    else:
        # Average text and media scores (simple approach)
        final_score = (text_score + media_score) / 2

    return round(final_score, 2)
