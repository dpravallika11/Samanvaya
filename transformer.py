import pandas as pd

def generate_transformation_code(mapping_dict, df_name="df"):
    """
    Generates pandas code representing the transformation.
    mapping_dict format: {"original_col": "suggested_col"}
    """
    # Filter out mappings where it's 'Unknown' or same name
    actual_mappings = {k: v for k, v in mapping_dict.items() if v != "Unknown" and k != v}
    
    if not actual_mappings:
        return f"# No transformations needed\n{df_name}_transformed = {df_name}.copy()"
    
    dict_str = "{\n"
    for k, v in actual_mappings.items():
        dict_str += f'    "{k}": "{v}",\n'
    dict_str += "}"
    
    code = f'{df_name}.rename(columns={dict_str}, inplace=True)'
    return code

def apply_transformation(df, mapping_dict):
    """
    Applies the transformation to the dataframe.
    """
    actual_mappings = {k: v for k, v in mapping_dict.items() if v != "Unknown" and k != v}
    transformed_df = df.rename(columns=actual_mappings)
    return transformed_df
