import random
import string

def generate_reference_id(length=16):
    """
    Generate a random alphanumeric reference ID of specified length.
    Default length is 16 characters.
    """
    # Define the character set: uppercase letters and digits
    characters = string.ascii_uppercase + string.digits
    
    # Generate a random string of the specified length
    reference_id = ''.join(random.choice(characters) for _ in range(length))
    
    return reference_id
