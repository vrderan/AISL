import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils.localization import get_string
from utils.state import navigate_to, navigate_back
from utils.data import get_category_signs

CATEGORIES = ["cat_abc", "cat_basics", "cat_greetings", "cat_animals", "cat_fingerspelling"]
CATEGORY_KEYS = {
    "cat_abc": "ABC",
    "cat_basics": "Basics",
    "cat_greetings": "Greetings",
    "cat_animals": "Animals",
    "cat_fingerspelling": "Fingerspelling"
}

# --- NEW MASTER FUNCTION ---
# This replaces both 'get_category_progress' and 'calculate_total_progress'
def get_language_stats(target_lang):
    """
    Calculates ALL progress stats for a language in a single pass.
    Returns:
       - total_learned (int): Total signs learned across all categories
       - total_signs (int): Total available signs
       - cat_progress (dict): A dictionary mapping category keys to their % completion
                              e.g. {'cat_abc': 50, 'cat_basics': 100}
    """
    stats = {
        "total_learned": 0,
        "total_signs": 0,
        "cat_progress": {}
    }
    
    # Get the user's progress for this language ONCE
    user_progress = st.session_state.user_progress.get(target_lang, {})
    
    for cat_key in CATEGORIES:
        # 1. Handle special cases (Fingerspelling has no fixed signs to count)
        if cat_key == "cat_fingerspelling":
            stats["cat_progress"][cat_key] = 0
            continue

        cat_internal = CATEGORY_KEYS.get(cat_key)
        
        # 2. Get signs for this category
        # (Make sure get_category_signs is cached in utils/data.py!)
        signs = get_category_signs(cat_internal, target_lang)
        cat_total = len(signs)
        
        if cat_total == 0:
            stats["cat_progress"][cat_key] = 0
            continue
            
        # 3. Calculate how many signs in this category are learned
        cat_learned = 0
        cat_data = user_progress.get(cat_internal, {})
        
        for sign in signs:
            if cat_data.get(sign, 0) >= 3:
                cat_learned += 1
        
        # 4. Update the GLOBAL totals
        stats["total_learned"] += cat_learned
        stats["total_signs"] += cat_total
        
        # 5. Save the CATEGORY specific percentage
        stats["cat_progress"][cat_key] = int((cat_learned / cat_total) * 100)
        
    return stats

# --- UPDATED RENDER FUNCTION ---
def render_language_column(lang_code):
    app_lang = st.session_state.app_lang
    lang_name = get_string(lang_code.lower(), app_lang)
    
    # CALL THE MASTER FUNCTION ONCE HERE
    stats = get_language_stats(lang_code)
    
    # Header
    st.markdown(f"<h3 style='text-align: center;'>{lang_name}</h3>", unsafe_allow_html=True)
    
    # Progress (Read from stats, don't recalculate!)
    st.markdown(
        f"<div style='text-align: center; color: gray; margin-bottom: 20px;'>"
        f"{stats['total_learned']}/{stats['total_signs']} {get_string('signs_learned', app_lang)}"
        f"</div>", 
        unsafe_allow_html=True
    )
    
    # Categories Loop
    for cat_key in CATEGORIES:
        localized_name = get_string(cat_key, app_lang)
        display_name = localized_name
        
        # ISL Bilingual Logic
        if lang_code == "ISL" and cat_key != "cat_fingerspelling" and app_lang == "en":
             name_he = get_string(cat_key, "he")
             display_name = f"{localized_name} ({name_he})"

        target_page = "learning"
        button_label = ""
        
        if cat_key == "cat_fingerspelling":
            button_label = display_name
            target_page = "fingerspelling"
        else:
            # READ PROGRESS FROM STATS (Fast!)
            progress = stats["cat_progress"].get(cat_key, 0)
            
            if progress >= 100:
                button_label = f"✅ {display_name} ({get_string('category_mastered', app_lang)})"
            else:
                button_label = f"{display_name} ({progress}%)"
        
        key = f"{lang_code}_{cat_key}"
        
        if st.button(button_label, key=key, use_container_width=True):
            st.session_state.target_lang = lang_code
            if cat_key != "cat_fingerspelling":
                st.session_state.category = CATEGORY_KEYS[cat_key]
            st.session_state.current_sign = None 
            navigate_to(target_page)
            st.rerun()

def render_language_selection():
    # CSS for spacing
    st.markdown("""
        <style>
        div.block-container {
            padding-top: 2rem !important;
            padding-bottom: 0rem !important;
            max-width: 95% !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Back Button
    with stylable_container(
        key="back_btn_container",
        css_styles="""
            button {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                width: 45px !important;
                height: 45px !important;
                padding: 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                color: inherit !important;
                transition: all 0.2s ease !important;
            }
            button:hover {
                background: rgba(128, 128, 128, 0.1) !important;
                transform: scale(1.05);
            }
            button span {
                font-size: 1.5rem !important;
            }
        """
    ):
        if st.button("", icon=":material/arrow_back:", key="back_btn"):
            navigate_back()
            st.rerun()

    # Main Title
    st.markdown(f"<h2 style='text-align: center;'>{get_string('select_learning_lang', st.session_state.app_lang)}</h2>", unsafe_allow_html=True)
    
    # Columns
    _, c1, _, c2, _ = st.columns([0.15, 0.8, 0.1, 0.8, 0.15])
    
    with c1:
        render_language_column("ASL")
        
    with c2:
        render_language_column("ISL")