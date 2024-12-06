from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_age(token_created_at):
    # Convert token_created_at (milliseconds since epoch) to datetime
    token_creation_date = datetime.fromtimestamp(token_created_at / 1000.0)
    
    # Get current datepo
    current_date = datetime.now()
    
    # Calculate the difference using relativedelta
    delta = relativedelta(current_date, token_creation_date)
    
    # Format the age as needed
    age_parts = []
    if delta.years > 0:
        age_parts.append(f"{delta.years}y")
    if delta.months > 0:
        age_parts.append(f"{delta.months}m")
    if delta.days > 0:
        age_parts.append(f"{delta.days}d")
    
    # Join parts with a space
    token_age = " ".join(age_parts) if age_parts else "0d"  # Default to "0d" if no age is found
    
    return token_age

def format_number(value_string):
    """Format a number into a more readable string with K or M suffix."""
    try:
        # Attempt to convert the value_string to a float
        value = float(value_string)
    except (ValueError, TypeError):
        # Return 'N/A' or a default value if conversion fails
        return 'N/A'

    # Format the number based on its magnitude
    if value < 1_000:
        return f"{value:.0f}"  # Return as is if less than 1000
    elif value < 1_000_000:
        return f"{value / 1_000:.1f}K"  # Convert to thousands
    else:
        return f"{value / 1_000_000:.1f}M"  # Convert to millions
