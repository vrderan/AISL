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

def get_category_progress(target_lang, category_key):
    cat_internal = CATEGORY_KEYS.get(category_key, category_key)
    signs = get_category_signs(cat_internal, target_lang)
    total_signs = len(signs)
    
    if total_signs == 0:
        return 0

    learned_count = 0
    if target_lang in st.session_state.user_progress:
        cat_data = st.session_state.user_progress[target_lang].get(cat_internal, {})
        for sign in signs:
            if cat_data.get(sign, 0) >= 3:
                learned_count += 1
    
    return int((learned_count / total_signs) * 100)

def calculate_total_progress(target_lang):
    # Internal category names (excluding custom fingerspelling)
    categories = ["ABC", "Basics", "Greetings", "Animals"]
    
    total_signs = 0
    for cat in categories:
        signs = get_category_signs(cat, target_lang)
        total_signs += len(signs)
        
    learned_count = 0
    if target_lang in st.session_state.user_progress:
        lang_data = st.session_state.user_progress[target_lang]
        for cat, signs_data in lang_data.items():
            for sign, count in signs_data.items():
                if count >= 3:
                    learned_count += 1
    
    return learned_count, total_signs

def render_language_column(lang_code):
    app_lang = st.session_state.app_lang
    lang_name = get_string(lang_code.lower(), app_lang)
    
    # Header
    st.markdown(f"<h3 style='text-align: center;'>{lang_name}</h3>", unsafe_allow_html=True)
    
    # Progress
    learned, total = calculate_total_progress(lang_code)
    st.markdown(f"<div style='text-align: center; color: gray; margin-bottom: 20px;'>{learned}/{total} {get_string('signs_learned', app_lang)}</div>", unsafe_allow_html=True)
    
    # Categories
    for cat_key in CATEGORIES:
        localized_name = get_string(cat_key, app_lang)
        display_name = localized_name
        
        # Bilingual display logic for ISL if needed, or just standard localized
        # Previous logic:
        if lang_code == "ISL":
            name_he = get_string(cat_key, "he")
            name_en = get_string(cat_key, "en")
            if cat_key != "cat_fingerspelling":
                 if app_lang == "he":
                    display_name = name_he
                 elif app_lang == "en":
                    display_name = f"{name_en} ({name_he})"
            else:
                display_name = localized_name
        
        target_page = "learning"
        is_completed = False
        
        if cat_key == "cat_fingerspelling":
            button_label = display_name
            target_page = "fingerspelling"
        else:
            progress = get_category_progress(lang_code, cat_key)
            if progress >= 100:
                is_completed = True
                button_label = f"✅ {display_name} ({get_string('category_mastered', app_lang)})"
            else:
                button_label = f"{display_name} ({progress}%)"
        
        # Styling for completed buttons?
        # User said: "the button of the category should show that"
        # I added checkmark and text.
        
        key = f"{lang_code}_{cat_key}"
        
        if st.button(button_label, key=key, use_container_width=True):
            st.session_state.target_lang = lang_code
            if cat_key != "cat_fingerspelling":
                st.session_state.category = CATEGORY_KEYS[cat_key]
            st.session_state.current_sign = None 
            navigate_to(target_page)
            st.rerun()

def render_language_selection():
    # Adjust page padding for a more compact look
    st.markdown("""
        <style>
        div.block-container {
            padding-top: 2rem !important; /* Reduced from default ~6rem */
            padding-bottom: 0rem !important;
            max-width: 95% !important; /* Optional: Use more screen width */
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Simple Back Button
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
                padding-bottom: 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                color: inherit !important;
                transition: all 0.2s ease !important;
            }
            button:hover {
                background: rgba(128, 128, 128, 0.1) !important; /* Light hover fill */
                border-color: rgba(128, 128, 128, 0.5) !important;
                transform: scale(1.05); /* Slight pop */
            }
            /* Fix for the icon inside the button */
            button span {
                font-size: 1.5rem !important;
            }
        """
    ):
        # Use the built-in material icon support (Streamlit 1.30+)
        if st.button("", icon=":material/arrow_back:", key="back_btn"):
            navigate_back()
            st.rerun()

    # Center Elements
    st.markdown(f"<h2 style='text-align: center;'>{get_string('select_learning_lang', st.session_state.app_lang)}</h2>", unsafe_allow_html=True)
    
    c1, c_spacer, c2 = st.columns([1, 0.2, 1])
    
    with c1:
        render_language_column("ASL")
        
    with c2:
        render_language_column("ISL")
