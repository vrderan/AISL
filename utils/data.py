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

# # Define the learning path order (Excluding fingerspelling)
# LEARNING_PATH = ["ABC", "Basics", "Greetings", "Animals"]

# def get_next_category(current_category):
#     """
#     Returns the next category ID, or None if this is the last one.
#     """
#     if current_category not in LEARNING_PATH:
#         print(f"⚠️ Warning: '{current_category}' not found in LEARNING_PATH: {LEARNING_PATH}")
#         return None
    
#     idx = LEARNING_PATH.index(current_category)
#     if idx + 1 < len(LEARNING_PATH):
#         return LEARNING_PATH[idx + 1]
#     return None # Finished all categories

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
    