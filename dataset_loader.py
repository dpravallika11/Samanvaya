import pandas as pd
import os
import json

def load_dataset(file_path):
    """
    Centralized function to load datasets of various tabular formats into a Pandas DataFrame.
    Supported formats: CSV, Excel, TSV, JSON, Parquet, Feather, XML.
    
    Returns:
        tuple: (DataFrame, None) on success, or (None, error_message) on failure.
    """
    if not os.path.exists(file_path):
        return None, f"File not found: {file_path}"
        
    ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
    
    try:
        if ext == 'csv':
            df = pd.read_csv(file_path)
        elif ext in ['xls', 'xlsx']:
            df = pd.read_excel(file_path)
        elif ext == 'tsv':
            df = pd.read_csv(file_path, sep='\t')
        elif ext == 'json':
            df = pd.read_json(file_path)
        elif ext == 'parquet':
            df = pd.read_parquet(file_path)
        elif ext == 'feather':
            df = pd.read_feather(file_path)
        elif ext == 'xml':
            df = pd.read_xml(file_path)
        else:
            return None, f"Unsupported file format: .{ext}"
            
        if df.empty:
            return None, "The uploaded file contains no data."
            
        return df, None
        
    except pd.errors.EmptyDataError:
        return None, "The file is empty or corrupted."
    except pd.errors.ParserError:
        return None, "Failed to parse the file. Please ensure it is correctly formatted."
    except ValueError as e:
        return None, f"Value error during loading: {str(e)}"
    except Exception as e:
        return None, f"An unexpected error occurred while loading the file: {str(e)}"
