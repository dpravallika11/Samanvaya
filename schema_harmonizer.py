import pandas as pd
from rapidfuzz import process, fuzz

def analyze_schemas(dfs):
    """
    Analyzes schemas of multiple DataFrames and suggests column mappings based on similarity.
    Returns a unified schema and mapping dictionary.
    """
    if not dfs:
        return {}

    all_columns = []
    for df in dfs:
        all_columns.extend(df.columns.tolist())
        
    # Naive approach: take the first df as the 'base'
    base_columns = dfs[0].columns.tolist()
    
    mapping_suggestions = [] # List of tuples: (original_col, suggested_col, dataset_index)
    
    for i, df in enumerate(dfs):
        if i == 0:
            continue
            
        cols = df.columns.tolist()
        for col in cols:
            # Find best match in base_columns
            match = process.extractOne(col, base_columns, scorer=fuzz.token_sort_ratio)
            
            # If match score > a threshold (e.g., 70), suggest mapping
            if match and match[1] > 70:
                suggested = match[0]
            else:
                suggested = col # Keep original if no good match
                
            mapping_suggestions.append({
                "dataset_index": i,
                "dataset_name": f"Dataset {i+1}",
                "original_col": col,
                "suggested_col": suggested,
                "confidence": match[1] if match else 0
            })
            
            # If no match, add to base for future matching (expanding schema)
            if suggested == col and col not in base_columns:
                base_columns.append(col)

    return {"base_schema": base_columns, "mappings": mapping_suggestions}

def apply_mappings(dfs, mappings_to_apply):
    """
    Applies column mappings and concatenates DataFrames.
    mappings_to_apply should be a list of dicts: {'dataset_index': int, 'original_col': str, 'new_col': str}
    """
    new_dfs = []
    
    # Store mappings by dataset
    mapping_by_dataset = {}
    for entry in mappings_to_apply:
        idx = entry['dataset_index']
        if idx not in mapping_by_dataset:
            mapping_by_dataset[idx] = {}
        mapping_by_dataset[idx][entry['original_col']] = entry['new_col']

    for i, df in enumerate(dfs):
        copied_df = df.copy()
        if i in mapping_by_dataset:
            copied_df.rename(columns=mapping_by_dataset[i], inplace=True)
        new_dfs.append(copied_df)

    # Combine all into one harmonized dataset
    try:
        harmonized_df = pd.concat(new_dfs, ignore_index=True)
    except Exception as e:
        # Fallback if concat fails
        print(f"Error concatenating: {e}")
        harmonized_df = new_dfs[0] if new_dfs else pd.DataFrame()
        
    return harmonized_df
