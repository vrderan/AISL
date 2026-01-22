import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import queue
import random
import os
import io
import functools # <--- NEW IMPORT

from utils.state import navigate_to, navigate_back, toggle_flag
from utils.styling import apply_video_mirror_style
from utils.localization import get_string
from utils.data import get_category_signs, get_sign_video_url
from streamlit_extras.stylable_container import stylable_container

# Ensure queue exists
if "quiz_result_queue" not in st.session_state:
    st.session_state.quiz_result_queue = queue.Queue()

def get_new_random_sign(current_sign, signs_list):
    """Selects a random sign different from the current one."""
    if not signs_list: return None
    if len(signs_list) == 1: return signs_list[0]
    available = [s for s in signs_list if s != current_sign]
    if not available: return signs_list[0]
    return random.choice(available)

# --- 1. STABLE FACTORY FUNCTION (Defined Globally) ---
# This function never changes, so WebRTC won't restart when we use it.
def create_quiz_processor(model, result_queue, category, target_lang):
    try:
        from utils.video import HandLandmarkProcessor
        
        return HandLandmarkProcessor(
            model=model,
            result_queue=result_queue,
            target_sign="", # Initialize with EMPTY sign (we update it dynamically)
            category=category,
            language=target_lang,
            translate_landmarks=True if category=='ABC' else False,
            scale_landmarks=True if category=='ABC' else False,
            hold_sign_duration = 1 if category=='ABC' else 0.1,
            success_cooldown = 1,
        )
    except Exception as e:
        print(f"CRITICAL VIDEO ERROR: {e}", flush=True)
        return None

# --- Fragment Listener ---
@st.fragment(run_every=0.5)
def poll_quiz_queue():
    try:
        if "quiz_result_queue" in st.session_state:
            result = st.session_state.quiz_result_queue.get_nowait()
            if result == "success":
                # st.toast(f"Correct! Moving to next sign...", icon="🎉")
                
                # Logic to update sign
                target_lang = st.session_state.target_lang
                category = st.session_state.category
                all_signs = get_category_signs(category, target_lang)
                current_sign = st.session_state.quiz_current_sign
                st.session_state.quiz_current_sign = get_new_random_sign(current_sign, all_signs)
                
                st.rerun()
    except queue.Empty:
        pass

def render_quiz():
    apply_video_mirror_style()
    poll_quiz_queue()
    
    target_lang = st.session_state.target_lang
    category = st.session_state.category
    all_signs = get_category_signs(category, target_lang)
    
    if "quiz_current_sign" not in st.session_state or st.session_state.quiz_current_sign not in all_signs:
        st.session_state.quiz_current_sign = get_new_random_sign(None, all_signs)
        
    current_sign = st.session_state.quiz_current_sign

    st.markdown("""
        <style>
        div.block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            max-width: 95% !important;
        }
        div[data-testid="stImage"] img {
            width: 100% !important;
            object-fit: contain !important;
            border-radius: 15px !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Back Button
    with stylable_container(
        key="back_btn_container",
        css_styles="""
            div[data-testid="stButton"] > button {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                width: 45px !important;
                min-width: 45px !important;
                height: 45px !important;
                padding: 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                color: inherit !important;
                transition: transform 0.2s ease !important;
            }
            div[data-testid="stButton"] > button:hover {
                background: rgba(128, 128, 128, 0.1) !important;
                transform: scale(1.1);
            }
            div[data-testid="stButton"] > button:active {
                background: rgba(128, 128, 128, 0.2) !important;
            }
            div[data-testid="stButton"] > button span[data-testid="stIconMaterial"] {
                font-size: 24px !important; 
            }
        """
    ):
        if st.button("", icon=":material/arrow_back:", key="back_btn"):
            navigate_back()
            st.rerun()

    st.markdown(f"<h2 style='text-align: center; margin-bottom: -25px; margin-top: -25px;'>{target_lang} {category} Quiz!</h2>", unsafe_allow_html=True)
    st.divider()

    left_col, mid_col, right_col = st.columns([1, 1.75, 1.25])

    with left_col:
        st.markdown("### Sign this:")
        st.markdown(f"<h1 style='color: #4da6ff;'>{current_sign}</h1>", unsafe_allow_html=True)
        st.write("") 
        
        if st.button("📌 Save for Later", use_container_width=True):
            toggle_flag(target_lang, category, current_sign)
            st.toast(f"Saved '{current_sign}'!", icon="📌")

        if st.button("⏭️ Skip", use_container_width=True):
            st.session_state.quiz_current_sign = get_new_random_sign(current_sign, all_signs)
            st.rerun()

    with mid_col:
        # Load stable resources
        from utils.model_loader import load_model
        model = load_model(target_lang, category)
        quiz_queue = st.session_state.quiz_result_queue
        
        # --- 2. CREATE STABLE PARTIAL ---
        # 'functools.partial' creates a function object that compares EQUAL 
        # as long as the arguments (model, queue, category) haven't changed.
        # This tricks WebRTC into thinking the factory is identical to the last run.
        stable_factory = functools.partial(
            create_quiz_processor, 
            model=model, 
            result_queue=quiz_queue, 
            category=category, 
            target_lang=target_lang
        )

        video_wrapper_key = "quiz_video_wrapper"
        wrapper_css = """
        div[data-testid="stVerticalBlock"] > div > div > div > video {
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        """
        
        with stylable_container(key=video_wrapper_key, css_styles=wrapper_css):
            ctx = webrtc_streamer(
                key="quiz_camera", 
                mode=WebRtcMode.SENDRECV,
                media_stream_constraints={
                    "video": {"width": 640, "height": 480, "frameRate": 30},
                    "audio": False
                },
                video_processor_factory=stable_factory, # <--- Pass the stable factory
                async_processing=True,
                desired_playing_state=True,
            )

            # --- 3. HOT SWAP TARGET ---
            # We instantly overwrite the empty target with the real one.
            if ctx.video_processor:
                ctx.video_processor.target_sign = current_sign

    with right_col:
        left_col2, right_col2 = st.columns([1, 1])
        with left_col2:
            st.markdown("### Need Help?")
        
        with right_col2:
            hint_key = f"show_hint_{current_sign}"
            if hint_key not in st.session_state:
                st.session_state[hint_key] = False

            if st.button("💡 I don't remember"):
                st.session_state[hint_key] = not st.session_state[hint_key]

        if st.session_state[hint_key]:
            if category == 'ABC':
                local_img_path = os.path.join("images", f"{current_sign}.png")
                if os.path.exists(local_img_path):
                    st.image(local_img_path, width='stretch')
                else:
                    st.info(f"No instructions available for '{current_sign}'.")
            else:
                video_info = get_sign_video_url(current_sign, target_lang)
                if video_info:
                    url, start_t = video_info
                    st.video(url, start_time=start_t, muted=True, autoplay=True)
                else:
                    st.info("No hint available.")
