import pandas as pd

def get_suggestions(df, col_name):
    """
    Returns a list of suggested prompts based on the column's data type.
    """
    if col_name not in df.columns:
        return ["Convert values", "Extract information"]

    # Try mapping to numeric just to check if it's convertible
    is_numeric = pd.api.types.is_numeric_dtype(df[col_name])
    if not is_numeric:
        try:
            pd.to_numeric(df[col_name].dropna().head(100))
            is_numeric = True
        except ValueError:
            pass

    if is_numeric:
        return [
            "Round values to nearest integer",
            "Convert negative values to positive",
            "Normalize values between 0 and 1",
            "Fill missing values with median"
        ]
    
    is_date = pd.api.types.is_datetime64_any_dtype(df[col_name])
    if not is_date and df[col_name].dtype == object:
         # simple heuristic check
         temp = df[col_name].dropna().astype(str)
         if temp.str.contains(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}').any():
             is_date = True
             
    if is_date:
        return [
            "Extract year from date",
            "Convert to format YYYY-MM-DD",
            "Extract month name"
        ]

    # Default to string/object
    return [
        "Convert text to uppercase",
        "Remove leading and trailing spaces",
        "Extract first word",
        "Fill missing values with 'Unknown'"
    ]
