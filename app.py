import streamlit as st
from utils.state import init_state
from utils.styling import load_css
import warnings

# Suppress the specific Protobuf warning
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")

# Page Config must be the first Streamlit command
st.set_page_config(layout="wide", page_title="AI-SL")

# Initialize session state
init_state()

# Load CSS based on theme
load_css()

# Views
from views import home

# Main App Routing
def main():

    if st.session_state.page == "home":
        home.render_home()
    elif st.session_state.page == "settings":
        import views.settings as settings_view
        settings_view.render_settings()
    elif st.session_state.page == "about":
        import views.about as about_view
        about_view.render_about()
    elif st.session_state.page == "language_selection":
        import views.language_selection as lang_select_view
        lang_select_view.render_language_selection()
    # elif st.session_state.page == "category_selection":
    #     import views.category_selection as cat_select_view
    #     cat_select_view.render_category_selection()
    elif st.session_state.page == "learning":
        import views.learning as learning_view
        learning_view.render_learning()
    elif st.session_state.page == "fingerspelling":
        import views.fingerspelling as fingerspelling_view
        fingerspelling_view.render_fingerspelling()
    elif st.session_state.page == "saved":
        import views.saved as saved_view
        saved_view.render_saved()
    elif st.session_state.page == "requests":
        import views.requests as requests_view
        requests_view.render_requests()
    else:
        st.write("404 - Page not found")
        if st.button("Go Home"):
            st.session_state.page = "home"
            st.rerun()

if __name__ == "__main__":
    main()