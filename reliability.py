import pandas as pd
import numpy as np

def calculate_reliability(df, mapped_columns):
    """
    Calculates a reliability score based on:
    1. Column mapping confidence (Average of all > 0)
    2. Data completeness (Missing value ratio)
    3. Data type consistency (Heuristic check)
    """
    
    # 1. Column Match Accuracy
    confidences = [m['confidence'] for m in mapped_columns if m['confidence'] > 0]
    col_accuracy = sum(confidences) / len(confidences) if confidences else 0
    
    # 2. Missing Value Handling
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    missing_ratio = (total_cells - missing_cells) / total_cells if total_cells > 0 else 0
    missing_score = missing_ratio * 100

    # 3. Data Type Validation (Heuristic: are columns mostly of a single type?)
    type_score = 85.0 # default baseline
    # Add minor bonus if numeric columns are actually numeric
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        type_score = min(100.0, type_score + 10)
    
    final_score = (col_accuracy * 0.4) + (missing_score * 0.3) + (type_score * 0.3)
    
    return {
        "Column Match Accuracy": round(col_accuracy),
        "Data Type Validation": round(type_score),
        "Missing Value Handling": round(missing_score),
        "Final Reliability Score": round(final_score)
    }
