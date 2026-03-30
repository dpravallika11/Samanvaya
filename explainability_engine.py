def generate_explanation(transformation_code, reasoning=""):
    """
    Explains the applied transformation code in human-readable format.
    """
    if reasoning:
        return reasoning
    return f"Applied code: {transformation_code}"

def explain_schema_alignment(source_col, target_col, confidence=100):
    return f"Mapped column '{source_col}' to '{target_col}' with {confidence}% confidence."
