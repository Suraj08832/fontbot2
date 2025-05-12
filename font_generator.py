from style_sets import STYLE_SETS

def generate_consistent_style(text: str, style_name: str) -> str:
    """Generate text in a consistent style based on the style name."""
    if style_name not in STYLE_SETS:
        return f"Style '{style_name}' not found."
    
    style_set = STYLE_SETS[style_name]
    result = []
    
    for char in text:
        if char.isalpha():
            # Convert to lowercase for lookup
            lookup_char = char.lower()
            if lookup_char in style_set:
                # If original char was uppercase, convert the styled char to uppercase
                styled_char = style_set[lookup_char]
                if char.isupper():
                    styled_char = styled_char.upper()
                result.append(styled_char)
            else:
                result.append(char)
        else:
            # Keep non-alphabetic characters unchanged
            result.append(char)
    
    return ''.join(result)

def get_available_styles() -> list:
    """Return a list of available style names."""
    return list(STYLE_SETS.keys())

def get_style_preview(style_name):
    """Generate a preview of a style using the alphabet."""
    if style_name not in STYLE_SETS:
        return f"Style '{style_name}' not found"
    
    style = STYLE_SETS[style_name]
    preview = ""
    for char in "abcdefghijklmnopqrstuvwxyz":
        if char in style:
            preview += style[char]
    return preview 