import pandas as pd
from rapidfuzz import process, fuzz

# A predefined dictionary of standard column names and their known variations
STANDARD_COLUMNS = {
    "Customer_Name": ["Cust_Name", "Client", "Customer", "User_Name", "CustNm", "Name", "Applicant"],
    "Phone_Number": ["ContactNo", "Mobile_No", "Contact", "PhoneNum", "Mobile", "Cell", "Phone"],
    "Amount": ["PricePaid", "Purchase_Value", "Price", "Cost", "Total", "Amount_Paid", "Value", "Sales"],
    "Email_Address": ["Email", "Email_Id", "Mail", "EmailId"],
    "Address": ["Location", "City", "State", "Address_Line", "Region"],
    "Date": ["Date_Of_Purchase", "Created_At", "Transaction_Date", "DOB", "OrderDate", "Date"]
}

def get_standard_columns():
    return list(STANDARD_COLUMNS.keys())

def map_columns(current_columns):
    """
    Takes a list of current column names and returns a list of dictionaries 
    with suggested mapping and confidence scores.
    """
    mapped_results = []
    
    for col in current_columns:
        best_match = None
        highest_score = 0
        
        # 1. Check exact match in standard columns
        if col in STANDARD_COLUMNS:
            mapped_results.append({
                "original": col,
                "suggested": col,
                "confidence": 100
            })
            continue
            
        # 2. Check dictionary mapping and fuzzy match variations
        for std_col, variations in STANDARD_COLUMNS.items():
            # Check exact variation match first
            if col.lower() in [v.lower() for v in variations]:
                if highest_score < 100:
                    best_match = std_col
                    highest_score = 100
                continue
                
            # Fuzzy match against variations
            match = process.extractOne(col, variations, scorer=fuzz.WRatio)
            if match:
                score = match[1]
                if score > highest_score:
                    highest_score = score
                    best_match = std_col
                    
            # Also fuzzy match against standard column name itself
            match_std = fuzz.WRatio(col, std_col)
            if match_std > highest_score:
                highest_score = match_std
                best_match = std_col
        
        # Determine strict threshold
        if highest_score > 60:
            suggested = best_match
            confidence = round(highest_score)
        else:
            suggested = "Unknown"
            confidence = 0
            
        mapped_results.append({
            "original": col,
            "suggested": suggested,
            "confidence": confidence
        })
        
    return mapped_results
