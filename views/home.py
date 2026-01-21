import streamlit as st
from utils.localization import get_string
from utils.state import navigate_to
from time import sleep

def render_home():
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
    # Center content
    st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>{}</h1>".format(get_string("welcome", st.session_state.app_lang)), unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem; color: gray;'>{}</h3>".format(get_string("subtitle", st.session_state.app_lang)), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 3, 3])
    
    with col2:
        if st.button(get_string("login", st.session_state.app_lang), use_container_width=True):
            navigate_to("language_selection")
            col2.empty()
            sleep(0.02)
            st.rerun()
        
        st.write("") 
        
        if st.button(get_string("signup", st.session_state.app_lang), use_container_width=True):
            navigate_to("language_selection")
            col2.empty()
            sleep(0.02)
            st.rerun()
            
        st.write("") 
        
        if st.button(get_string("guest", st.session_state.app_lang), use_container_width=True):
            navigate_to("language_selection")
            col2.empty()
            sleep(0.02)
            st.rerun()
        
        st.write("") 
        
        # Settings and About buttons row
        col_set, col_abt = st.columns(2)
        with col_set:
             if st.button(f"⚙️ {get_string('settings_title', st.session_state.app_lang)}", key="settings_btn", use_container_width=True):
                navigate_to("settings")
                col2.empty()
                sleep(0.02)
                st.rerun()
        with col_abt:
             if st.button(f"ℹ️ {get_string('about_title', st.session_state.app_lang)}", key="about_btn", use_container_width=True):
                navigate_to("about")
                col2.empty()
                sleep(0.02)
                st.rerun()

        st.write("")
        
        # Saved and Request buttons row
        col_saved, col_req = st.columns(2)
        with col_saved:
            if st.button("Saved", use_container_width=True):
                navigate_to("saved")
                col2.empty()
                sleep(0.02)
                st.rerun()
        with col_req:
            if st.button("Want More?", use_container_width=True):
                navigate_to("requests")
                col2.empty()
                sleep(0.02)
                st.rerun()
