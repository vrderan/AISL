import streamlit as st

# Define signs for each category
SIGNS_DB = {
    "ABC": [], # Populated dynamically below
    "Basics": ["Hello", "Goodbye", "Thank You", "Please", "Yes", "No", "Sorry", "I Love You"],
    "Questions": ["Who", "What", "When", "Where", "Why", "How"],
    "Animals": ["Dog", "Cat", "Horse", "Bird", "Fish", "Elephant", "Giraffe"]
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
    
    "Who": "מי",
    "What": "מה",
    "When": "מתי",
    "Where": "איפה",
    "Why": "למה",
    "How": "איך",
    
    "Dog": "כלב",
    "Cat": "חתול",
    "Horse": "סוס",
    "Bird": "ציפור",
    "Fish": "דג",
    "Elephant": "פיל",
    "Giraffe": "ג'ירפה",
}

# Dictionary mapping sign IDs to YouTube URLs, start times, and end times
SIGN_VIDEOS = {
    "Thank You": ("https://youtu.be/3YJ6hyyL4nw?si=RSHgvDhViEPq5vU1", 3, None),
    "Please": ("https://youtu.be/o_qBUh7ZKSQ?si=ltXErfNhp8SRLDl8", 13, 22),
    "Yes": ("https://youtu.be/zKDPRl7Vv0I?si=CT4DLne2pGjXh89C", 13, 20),
    "No": ("https://youtu.be/zKDPRl7Vv0I?si=T81ck8Djxg472u2X", 22, 30),
    "Sorry": ("https://youtu.be/AMGGpAKltS0?si=0GjWBo4BatjXCkA7&t=12", 12, 18),
    "I Love You": ("https://youtu.be/jzJjdvTF10A?si=O6Wdr3qPFHZGWXFx", 4, 22),
    "Hello": ("https://youtu.be/SsLvqfTXo78?si=yXHCLarLXjqdYErM", 4, 10),
    "Goodbye": ("https://youtu.be/SwhzH7GLL1k?si=VATv7AftByGUhPkk", 0, None),
    "תודה": ("https://youtu.be/iHl0fxyPeZI?si=GjWQ0fHXZlHmOkfz", 0, None),
    "בבקשה": ("https://youtu.be/7DZEsCrtmb8?si=iuaHUkDK5puR9BZv", 6, 13),
    "כן": ("https://youtu.be/GDV3K8BXSQI?si=jKPpCmfhtt26PRyT", 62, 64),
    "לא": ("https://youtu.be/qDVpa3yY_NU?si=m5XBim2MDZxNOBcZ", 0, None),
    "סליחה": ("https://youtu.be/jotyf-OKyl4?si=40e8dKFtHivtAMe0", 0, None),
    "אהבה": ("https://youtu.be/n6wR5ZMfMgs?si=nJ0j8rcNON0jXX1M", 0, None),
    "שלום": ("https://youtu.be/_LM_H7FfOmg?si=HYN8n2GURqVQ3pWr", 0, None),
    "להתראות": ("https://youtu.be/GDV3K8BXSQI?si=jKPpCmfhtt26PRyT", 59, 62),
    
    "Who": ("https://youtu.be/MxWGiBnIBZk?si=kUGY7LSjO48XLsFh", 68, 73),
    "What": ("https://youtu.be/MxWGiBnIBZk?si=kUGY7LSjO48XLsFh", 81, 95),
    "When": ("https://youtu.be/MxWGiBnIBZk?si=kUGY7LSjO48XLsFh", 122, 137),
    "Where": ("https://youtu.be/MxWGiBnIBZk?si=kUGY7LSjO48XLsFh", 138, 148),
    "Why": ("https://youtu.be/MxWGiBnIBZk?si=kUGY7LSjO48XLsFh", 151, 161),
    "How": ("https://youtu.be/DTPifvLp3q0?si=eEkfbFE7yi2RRqKZ", 9, None),
    "מי": ("https://youtu.be/jnyt7c_VH34?si=GLE-pn9QI5z8Ootb", 0, None),
    "מה": ("https://youtu.be/YqH8jMLYWV0?si=4Nq0quxHDfU0rXMe", 0, None),
    "מתי": ("https://youtu.be/NjQPNh5Fb-s?si=TlAKi6_dXGPJMEL7", 0, None),
    "איפה": ("https://youtu.be/ED0CnKqggZk?si=ARX7HzJCYavYHqIW", 0, None),
    "למה": ("https://youtu.be/i079qMpPEZM?si=g54LfUSSMx51unMR", 0, None),
    "איך": ("https://youtu.be/uFoTQwjdVh0?si=7qaL_xfyxpjkeoA_", 0, None),
    
    "Dog": ("https://youtu.be/mtkRr-5mK9M?si=8qgbgAYyLKisHhcp", 2, 5),
    "Cat": ("https://youtu.be/kEXO6dg12Mc?si=m44R861CVxh1ykPk", 0, 5),
    "Horse": ("https://youtu.be/fN4baaByX9A?si=94f_ozWQCGYq5gyA", 289, 297),
    "Bird": ("https://youtu.be/fN4baaByX9A?si=pKiUxRbBlu7IUdBo", 94, 100),
    "Fish": ("https://youtu.be/fN4baaByX9A?si=WTjbaTs5FY8aOtvK", 211, 218),
    "Elephant": ("https://youtu.be/fN4baaByX9A?si=WTjbaTs5FY8aOtvK", 202, 210),
    "Giraffe": ("https://youtu.be/fN4baaByX9A?si=WTjbaTs5FY8aOtvK", 248, 256),
    "כלב": ("https://youtu.be/SFsFbd9qDo4?si=_gVqnB3QHT_keob_", 0, None),
    "חתול": ("https://youtu.be/f7_Ln04YLJE?si=1OmCged8z1kGuvEW", 0, None),
    "סוס": ("https://youtu.be/Kb1FcO5X064?si=vXy3c16KxIbrMwuG", 0, None),
    "ציפור": ("https://youtu.be/NnInrfyXpUw?si=8uOZ9kfoTuO8OAkQ", 0, None),
    "דג": ("https://youtu.be/UT_IpGBp31Q?si=ifG0nKA-QDl8rIXQ", 0, None),
    "פיל": ("https://youtu.be/6cdDzFrsY0U?si=_lEoCG0bnkr7LV_X", 0, None),
    "ג'ירפה": ("https://youtu.be/51ia70NXN4k?si=6eAxLe27ByzWphwz", 0, None),
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

@st.cache_data
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
    