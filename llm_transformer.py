import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Setup Gemini API
api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

def generate_transformation_code(col_name, sample_values, prompt):
    """
    Sends column name, sample values, and user prompt to Gemini API.
    Returns generated pandas code and logical reasoning.
    """
    if not api_key:
        # Fallback for hackathon demo if no API key is set
        return f"df['{col_name}'] = df['{col_name}'].astype(str) + ' (Simulated API Mode)' ", "No Gemini API key found. Defaulted to mock transformation."
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = f"""
        You are an expert Data Engineer AI. 
        You are given a pandas DataFrame named `df`. 
        The user wants to transform a specific column based on a natural language prompt.
        
        Column name: '{col_name}'
        Sample values from this column: {sample_values}
        
        User prompt: {prompt}
        
        Generate ONLY Python Pandas code to apply this transformation to `df` and a brief reasoning.
        Format your exact output as exactly two parts separated by '|||'.
        
        Part 1: The single line or block of python code (without python markdown backticks).
        Part 2: The explanation of what the code does.
        
        Example output format:
        df['{col_name}'] = df['{col_name}'] / 30.48 ||| Divided by 30.48 to convert centimeters to feet.
        """
        
        response = model.generate_content(system_prompt)
        text = response.text.strip()
        
        if "|||" in text:
            parts = text.split("|||")
            code = parts[0].strip().replace("```python", "").replace("```", "").strip()
            reasoning = parts[1].strip()
            return code, reasoning
        else:
            code = text.replace("```python", "").replace("```", "").strip()
            return code, "Generated Python pandas transformation code."
            
    except Exception as e:
        return f"# Error during LLM generation: {str(e)}", "Failed to connect to the LLM."
