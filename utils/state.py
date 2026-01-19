import streamlit as st
from utils.model_loader import load_model

def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "history" not in st.session_state:
        st.session_state.history = []
    if "app_lang" not in st.session_state:
        st.session_state.app_lang = "en"
    if "sound_on" not in st.session_state:
        st.session_state.sound_on = True
    if "theme" not in st.session_state:
        st.session_state.theme = "light"  # placeholder
    if "target_lang" not in st.session_state:
        st.session_state.target_lang = None
    if "category" not in st.session_state:
        st.session_state.category = None
    if "current_sign" not in st.session_state:
        st.session_state.current_sign = None
    if "user_progress" not in st.session_state:
        # Structure: { target_lang: { category: { sign: count } } }
        st.session_state.user_progress = {}
    if "flagged_signs" not in st.session_state:
        # List of dicts: {"lang": "...", "category": "...", "sign": "..."}
        st.session_state.flagged_signs = []
    if "video_key_id" not in st.session_state:
        st.session_state.video_key_id = 0

def get_progress(target_lang, category, sign):
    lang_prog = st.session_state.user_progress.get(target_lang, {})
    # print(f'lang_prog: {lang_prog}')
    cat_prog = lang_prog.get(category, {})
    # print(f'cat_prog: {cat_prog}')
    return cat_prog.get(sign, 0)

def increment_progress(target_lang, category, sign):
    if target_lang not in st.session_state.user_progress:
        st.session_state.user_progress[target_lang] = {}
    if category not in st.session_state.user_progress[target_lang]:
        st.session_state.user_progress[target_lang][category] = {}
    
    current = st.session_state.user_progress[target_lang][category].get(sign, 0)
    if current < 3:
        st.session_state.user_progress[target_lang][category][sign] = current + 1

def decrement_progress(target_lang, category, sign):
    if target_lang not in st.session_state.user_progress:
        return # Nothing to decrement
    if category not in st.session_state.user_progress[target_lang]:
        return
    
    current = st.session_state.user_progress[target_lang][category].get(sign, 0)
    if current > 0:
        st.session_state.user_progress[target_lang][category][sign] = current - 1

def toggle_flag(target_lang, category, sign):
    # Check if exists
    exists = False
    for item in st.session_state.flagged_signs:
        if item["lang"] == target_lang and item["category"] == category and item["sign"] == sign:
            exists = True
            break
    
    if not exists:
        st.session_state.flagged_signs.append({
            "lang": target_lang,
            "category": category,
            "sign": sign
        })

def navigate_to(page):
    # Don't push to history if we are already on that page (avoids loops) or if it's the same
    if st.session_state.page != page:
        st.session_state.history.append(st.session_state.page)
    
    # Force video reload if navigating to learning
    if page == "learning":
        if "video_key_id" not in st.session_state:
             st.session_state.video_key_id = 0
        st.session_state.video_key_id += 1
        
    st.session_state.page = page

def navigate_back():
    if st.session_state.history:
        previous_page = st.session_state.history.pop()
        
        # Also force reload if going back to learning
        if previous_page == "learning":
             load_model.clear()
             if "video_key_id" not in st.session_state:
                 st.session_state.video_key_id = 0
             st.session_state.video_key_id += 1
             
        st.session_state.page = previous_page
    else:
        st.session_state.page = "home"
