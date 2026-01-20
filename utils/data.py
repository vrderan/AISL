# Define signs for each category
SIGNS_DB = {
    "ABC": [], # Populated dynamically below
    "Basics": ["Thank You", "Please", "Yes", "No", "Sorry", "I Love You"],
    "Greetings": ["Hello", "Goodbye", "Good Morning", "Good Night", "Nice to meet you"],
    "Animals": ["Dog", "Cat", "Horse", "Bird", "Fish"]
}

# Full alphabets
ASL_ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
ISL_ALPHABET = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת']

SIGNS_HE = {
    "Thank You": "תודה",
    "Please": "בבקשה",
    "Yes": "כן",
    "No": "לא",
    "Sorry": "סליחה",
    "I Love You": "אהבה",
    "Hello": "שלום",
    "Goodbye": "להתראות",
    "Good Morning": "בוקר טוב",
    "Good Night": "לילה טוב",
    "Nice to meet you": "נעים להכיר",
    "Dog": "כלב",
    "Cat": "חתול",
    "Horse": "סוס",
    "Bird": "ציפור",
    "Fish": "דג"
}

# Dictionary mapping sign IDs to YouTube URLs
SIGN_VIDEOS = {
    "Thank You": ("https://youtu.be/3YJ6hyyL4nw?si=RSHgvDhViEPq5vU1", 3),
    "Please": ("https://youtu.be/o_qBUh7ZKSQ?si=ltXErfNhp8SRLDl8", 13),
    "Yes": ("https://youtu.be/zKDPRl7Vv0I?si=CT4DLne2pGjXh89C", 13),
    "No": ("https://youtu.be/zKDPRl7Vv0I?si=T81ck8Djxg472u2X", 22),
    "Sorry": ("https://youtu.be/AMGGpAKltS0?si=0GjWBo4BatjXCkA7", 12),
    "I Love You": ("https://youtu.be/jzJjdvTF10A?si=O6Wdr3qPFHZGWXFx", 4),
    "תודה": ("https://youtu.be/iHl0fxyPeZI?si=GjWQ0fHXZlHmOkfz", 0),
    "בבקשה": ("https://youtu.be/7DZEsCrtmb8?si=iuaHUkDK5puR9BZv", 6),
    "כן": ("https://youtu.be/GDV3K8BXSQI?si=txejOG8tHTuP6F2D", 62),
    "לא": ("https://youtu.be/qDVpa3yY_NU?si=m5XBim2MDZxNOBcZ", 0),
    "סליחה": ("https://youtu.be/jotyf-OKyl4?si=40e8dKFtHivtAMe0", 0),
    "אהבה": ("https://youtu.be/n6wR5ZMfMgs?si=nJ0j8rcNON0jXX1M", 0),
}

def get_next_category(current_category, target_lang):
    """
    Returns the next un-mastered category ID.
    It searches sequentially starting from the current category.
    If it reaches the end, it wraps around to the beginning.
    Returns None if ALL categories are mastered.
    """
    from utils.state import get_progress  # Import here to avoid circular dependency
    
    categories = list(SIGNS_DB.keys())
    
    if current_category not in categories:
        return categories[0] if categories else None
    
    current_idx = categories.index(current_category)
    
    # Create a search order: [Next, Next+1, ... End, Start, Start+1, ... Prev]
    # This ensures we prefer moving forward, but will wrap around to find missed levels.
    search_order = categories[current_idx+1:] + categories[:current_idx+1]
    
    for cat in search_order:
        # Determine signs list (Handle ABC dynamic logic)
        if cat == "ABC":
            signs = ASL_ALPHABET if target_lang == "ASL" else ISL_ALPHABET
        else:
            signs = SIGNS_DB.get(cat, [])
            
        # Check if this category is mastered
        # A category is mastered ONLY if ALL signs have progress >= 3
        is_mastered = True
        for sign in signs:
            if get_progress(target_lang, cat, sign) < 3:
                is_mastered = False
                break # Found an un-mastered sign, so the category is incomplete
        
        # If we found a category that is NOT mastered, return it immediately
        if not is_mastered:
            return cat
            
    # If we loop through everything and find nothing un-mastered
    return None

def get_category_signs(category, target_lang):
    if category == "ABC":
        if target_lang == "ISL":
            return ISL_ALPHABET
        else:
            return ASL_ALPHABET
    return SIGNS_DB.get(category, [])

def get_sign_display_name(sign, target_lang):
    """
    Returns the display name based on target_lang:
    - ISL -> Hebrew (if in SIGNS_HE or is Hebrew letter)
    - ASL -> English (default)
    """
    if target_lang == "ISL":
        # Check if it's already a Hebrew letter (simple check)
        if sign in ISL_ALPHABET:
            return sign
        return SIGNS_HE.get(sign, sign)
    return sign

def get_sign_video_url(sign, target_lang):
    """Returns the URL if it exists, else None."""
    if target_lang == "ISL":
        return SIGN_VIDEOS.get(SIGNS_HE.get(sign, sign))
    return SIGN_VIDEOS.get(sign)
    