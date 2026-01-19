import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils.localization import get_string
from utils.state import navigate_to, navigate_back

def render_requests():
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

    st.header("Request Signs")
    
    st.write("Want to learn a sign that isn't here? Let us know!")
    
    request_text = st.text_area("Enter your request:")
    
    if st.button("Submit Request"):
        if request_text.strip():
            st.success("Request submitted! Thank you.")
            # Logic to save request would go here
        else:
            st.warning("Please enter some text.")
