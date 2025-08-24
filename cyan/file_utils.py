"""
Utility functions for file validation and processing
"""
import os
from typing import Optional, Tuple, Union, List

def validate_ipa_file(file_path: str, check_exists: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validates an IPA file path.
    
    Args:
        file_path: The path to the IPA file
        check_exists: Whether to check if the file exists on disk
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if valid, False otherwise
        - error_message: None if valid, error message otherwise
    """
    # Check if the path is a string
    if not isinstance(file_path, str):
        return False, "Invalid file type. Expected a string file path."
    
    # Check if the path is empty
    if not file_path:
        return False, "File path is empty."
        
    # Check if the path is too short to be valid
    if len(file_path) < 5:  # Minimum would be "a.ipa"
        return False, f"Invalid file path. Path is too short ({len(file_path)} characters)."
    
    # Check for valid extensions
    valid_extensions = ['.ipa', '.tipa']  # Add .tipa for TrollStore support
    has_valid_ext = False
    
    for ext in valid_extensions:
        if file_path.lower().endswith(ext):
            has_valid_ext = True
            break
    
    if not has_valid_ext:
        ext_list = ', '.join(valid_extensions)
        return False, f"Invalid file type. File must end with one of these extensions: {ext_list}"
    
    # Check if the file exists (optional)
    if check_exists and not os.path.exists(file_path):
        return False, f"File not found: `{file_path}`"
    
    # All checks passed
    return True, None
