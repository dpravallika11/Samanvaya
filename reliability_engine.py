from rapidfuzz import fuzz

def calculate_reliability(transformations):
    """
    Computes a reliability/confidence score for the applied transformations based on:
    - Code execution success
    - Semantic similarity between user prompt and generated code keywords (simulated heuristic)
    """
    
    if not transformations:
        return 100
        
    total_score = 0
    
    for t in transformations:
        score = 100
        status = t.get('status', 'Failed')
        mode = t.get('mode', 'Manual')
        
        if status == 'Failed':
            score -= 40  # Heavy penalty for execution error
        
        if mode == 'AI':
            # Slight uncertainty deduction for AI-generated code
            score -= 5
            
            # Simulated confidence based on prompt similarity to code components
            prompt = t.get('prompt', '').lower()
            code = t.get('code', '').lower()
            
            # Simple heuristic: if code contains common python/pandas terms related to the prompt
            if prompt:
                similarity = fuzz.partial_ratio(prompt, code)
                # If similarity is very low, maybe the AI hallucinated something completely different
                if similarity < 30:
                    score -= 10
        
        total_score += max(10, min(100, score))
        
    return int(total_score / len(transformations))
