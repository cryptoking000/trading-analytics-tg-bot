from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_token_age(token_created_at):
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

# Example usage
token_created_at = 1690335081000  # Example timestamp in milliseconds
token_age = calculate_token_age(token_created_at)
print(f"Token Age: {token_age}")