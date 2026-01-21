import streamlit as st

def get_css(theme):
    if theme == "dark":
        return """
        <style>
        /* --- 1. GLOBAL TEXT COLOR FIX (DARK MODE) --- */
        /* Force white text on main elements for readability */
        html, body, .stApp, h1, h2, h3, h4, h5, h6, p, label, li, span,
        [data-testid="stMarkdownContainer"] p, 
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] li {
            color: #FAFAFA !important;
        }

        /* --- 2. DARK AURORA BACKGROUND --- */
        .stApp {
            background: linear-gradient(180deg, #141E30 0%, #243B55 100%);
            background-attachment: fixed;
        }

        /* --- 3. INPUTS & SELECTBOXES --- */
        .stTextInput > div > div > input, 
        .stSelectbox > div > div > div {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }
        /* Dropdown menu items */
        ul[data-testid="stSelectboxVirtualDropdown"] li {
            background-color: #243B55 !important;
            color: white !important;
        }

        /* --- 4. BUTTONS & POPOVERS --- */
        .stButton > button {
            background-color: rgba(255, 255, 255, 0.1);
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            background-color: rgba(255, 255, 255, 0.25);
            border-color: white;
            transform: translateY(-2px);
        }

        /* Fix Popover Button (The small button that opens the menu) */
        div[data-testid="stPopover"] > button {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }

        /* --- 5. EXPANDER & INSTRUCTIONS --- */
        /* Header of the expander */
        div[data-testid="stExpander"] details summary {
            color: #FAFAFA !important;
        }
        div[data-testid="stExpander"] details summary:hover {
            color: #bdc3c7 !important;
        }
        /* Content inside expander */
        div[data-testid="stExpander"] details div {
            color: #FAFAFA !important;
        }
        .streamlit-expanderContent {
            background-color: transparent !important;
        }
        </style>
        """
    else:
        # --- LIGHT THEME ---
        return """
        <style>
        html, body, [class*="css"] {
            font-size: 18px;
        }

        /* --- LIGHT AURORA BACKGROUND --- */
        .stApp {
            background: linear-gradient(to top, #accbee 0%, #e7f0fd 100%);
            background-attachment: fixed;
            /* Sets the default text color for the page, but allows overrides (like buttons) */
            color: #2c3e50; 
        }

        /* Header specific styling */
        h1, h2, h3 { 
            color: #2c3e50 !important; 
        }

        /* --- BUTTONS (Force White Text) --- */
        .stButton > button {
            background: linear-gradient(to right, #6a11cb 0%, #2575fc 100%);
            color: white !important; /* IMPORTANT: Keeps button text white */
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
            color: white !important;
        }
        
        /* Fix Popover Buttons in Light Mode if needed */
        div[data-testid="stPopover"] > button {
            color: #2c3e50; /* Or standard dark */
        }
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