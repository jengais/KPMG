# part1/validator.py

from typing import Dict, Any

def count_filled_fields(data: Dict[str, Any]) -> int:
    """
    Recursively counts all non-empty fields in the JSON structure.
    """
    count = 0
    for value in data.values():
        if isinstance(value, dict):
            count += count_filled_fields(value)
        elif value and str(value).strip():  # Check if value is non-empty
            count += 1
    return count

def calculate_extraction_stats(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates statistics about the completeness of extracted data.
    """
    # Count total fields (including nested ones)
    total_fields = 0
    for value in data.values():
        if isinstance(value, dict):
            total_fields += len(value)
        else:
            total_fields += 1

    # Count filled fields
    filled_fields = count_filled_fields(data)
    
    # Calculate completion percentage
    completion_percentage = (filled_fields / total_fields * 100) if total_fields > 0 else 0
    
    return {
        "total_fields": total_fields,
        "filled_fields": filled_fields,
        "empty_fields": total_fields - filled_fields,
        "completion_percentage": round(completion_percentage, 2)
    } 