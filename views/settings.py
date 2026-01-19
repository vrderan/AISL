import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils.localization import get_string
from utils.state import navigate_to, navigate_back

def render_settings():
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

    st.header(get_string("settings_title", st.session_state.app_lang))
    
    # App Language
    lang_options = {"English": "en", "Hebrew": "he"}
    # Reverse lookup for display
    current_lang_display = [k for k, v in lang_options.items() if v == st.session_state.app_lang][0]
    
    selected_lang = st.selectbox(
        get_string("language", st.session_state.app_lang),
        options=list(lang_options.keys()),
        index=list(lang_options.keys()).index(current_lang_display)
    )
    
    if lang_options[selected_lang] != st.session_state.app_lang:
        st.session_state.app_lang = lang_options[selected_lang]
        st.rerun()

    # Sound On/Off
    st.session_state.sound_on = st.toggle(get_string("sound", st.session_state.app_lang), value=st.session_state.sound_on)

    # Theme
    is_dark = st.session_state.theme == "dark"
    # Using key to automatically update state is tricky if we want to rerun immediately for CSS
    # so we manually check return value
    new_theme_val = st.toggle(get_string("theme", st.session_state.app_lang), value=is_dark)
    
    new_theme = "dark" if new_theme_val else "light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.markdown("---")
    # Redundant bottom back button
    if st.button(get_string("back_home", st.session_state.app_lang)):
        navigate_to("home")
        st.rerun()
