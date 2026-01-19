import streamlit as st

def get_css(theme):
    if theme == "dark":
        return """
        <style>
        /* Force text color for generic elements to avoid black-on-black */
        html, body, .stApp, .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label, div, span {
            color: #FAFAFA !important;
        }

        .stApp {
            background-color: #121212;
        }

        /* Input fields, select boxes background */
        .stTextInput > div > div > input, .stSelectbox > div > div > div {
            background-color: #333333;
            color: white;
        }

        /* Button Styling for Dark Mode */
        .stButton > button {
            background-color: #333333;
            color: #FFFFFF !important;
            border: 1px solid #555555;
            border-radius: 12px;
            transition: all 0.3s;
            font-size: 1.2rem;
            padding: 0.75rem 1.5rem;
            min-height: 3rem;
        }
        .stButton > button:hover {
            background-color: #555555;
            border-color: #777777;
            color: #FFFFFF !important;
        }
        
        h1 { font-size: 3rem; }
        h2 { font-size: 2.5rem; }
        h3 { font-size: 2rem; }
        p { font-size: 1.2rem; }
        </style>
        """
    else:
        # Colorful/Light Theme
        return """
        <style>
        html, body, [class*="css"] {
            font-size: 18px;
        }
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #000000;
        }
        /* Button Styling for Light Mode */
        .stButton > button {
            background: linear-gradient(to right, #6a11cb 0%, #2575fc 100%);
            color: white;
            border: none;
            border-radius: 16px;
            padding: 0.75rem 1.5rem;
            font-weight: bold;
            font-size: 1.2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            min-height: 3rem;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
            color: white;
        }

        h1 { font-size: 3rem; color: #2c3e50; }
        h2 { font-size: 2.5rem; color: #2c3e50; }
        h3 { font-size: 2rem; color: #2c3e50; }
        p { font-size: 1.2rem; }
        </style>
        """

def load_css():
    theme = st.session_state.get("theme", "light")
    st.markdown(get_css(theme), unsafe_allow_html=True)

def apply_video_mirror_style():
    st.markdown("""
    <style>
    video {
        transform: scaleX(-1);
        -webkit-transform: scaleX(-1);
    }
    </style>
    """, unsafe_allow_html=True)
