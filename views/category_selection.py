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
    # Fix progress calculation: Use actual sign count
    cat_internal = CATEGORY_KEYS.get(category_key, category_key)
    
    # Get actual signs for this category
    signs = get_category_signs(cat_internal, target_lang)
    total_signs = len(signs)
    
    if total_signs == 0:
        return 0

    learned_count = 0
    if target_lang in st.session_state.user_progress:
        cat_data = st.session_state.user_progress[target_lang].get(cat_internal, {})
        for sign in signs:
            # Check if this specific sign is mastered
            if cat_data.get(sign, 0) >= 3:
                learned_count += 1
    
    return int((learned_count / total_signs) * 100)

def render_category_selection():
    # Adjust page padding for a more compact look
    st.markdown("""
        <style>
        div.block-container {
            padding-top: 1rem !important; /* Reduced from default ~6rem */
            padding-bottom: 1rem !important;
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

    # Center Title and Subtitle
    st.markdown(f"<h2 style='text-align: center;'>{get_string('select_category', st.session_state.app_lang)}</h2>", unsafe_allow_html=True)
    
    target_lang = st.session_state.target_lang
    app_lang = st.session_state.app_lang
    
    st.markdown(f"<p style='text-align: center; color: gray;'>Target Language: {target_lang}</p>", unsafe_allow_html=True)
    
    # Centered list for categories
    # Use columns to center the content: Spacer, Content, Spacer
    c_left, c_center, c_right = st.columns([1, 2, 1])
    
    with c_center:
        for cat_key in CATEGORIES:
            localized_name = get_string(cat_key, app_lang)
            display_name = localized_name
            
            if target_lang == "ISL":
                name_he = get_string(cat_key, "he")
                name_en = get_string(cat_key, "en")
                if cat_key != "cat_fingerspelling": # Don't duplicate for fingerspelling if redundant
                     if app_lang == "he":
                        display_name = name_he
                     elif app_lang == "en":
                        display_name = f"{name_en} ({name_he})"
                else:
                    display_name = localized_name

            if cat_key == "cat_fingerspelling":
                button_label = display_name
                target_page = "fingerspelling"
            else:
                progress = get_category_progress(target_lang, cat_key)
                button_label = f"{display_name} ({progress}%)"
                target_page = "learning"
            
            if st.button(button_label, key=cat_key, use_container_width=True):
                if cat_key != "cat_fingerspelling":
                    st.session_state.category = CATEGORY_KEYS[cat_key]
                st.session_state.current_sign = None 
                navigate_to(target_page)
                st.rerun()
