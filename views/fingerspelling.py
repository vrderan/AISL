import streamlit as st
import os
import re
import queue

try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
    HAS_WEBRTC = True
except ImportError:
    HAS_WEBRTC = False

from streamlit_extras.stylable_container import stylable_container
from utils.localization import get_string
from utils.state import navigate_back
from utils.video import HandLandmarkProcessor
from utils.data import ASL_ALPHABET, ISL_ALPHABET
from utils.model_loader import load_model

def render_fingerspelling():
    # 1. Initialize State
    if "fs_word" not in st.session_state:
        st.session_state.fs_word = ""
    if "fs_index" not in st.session_state:
        st.session_state.fs_index = 0
    if "fs_active" not in st.session_state:
        st.session_state.fs_active = False
    if "result_queue" not in st.session_state:
        st.session_state.result_queue = queue.Queue()

    HEBREW_MAPPING = {'ך': 'כ',
                      'ם': 'מ',
                      'ן': 'נ',
                      'ף': 'פ',
                      'ץ': 'צ'}
    
    # 2. Load Model & Prepare Variables
    target_lang = st.session_state.target_lang
    category = "ABC" 
    
    # We load the model here (cached via the loader)
    model = load_model(target_lang, category)
    
    # Variables for the Factory
    current_queue = st.session_state.result_queue
    
    # Determine current target letter
    current_target = None
    if st.session_state.fs_active and st.session_state.fs_index < len(st.session_state.fs_word):
        current_target = st.session_state.fs_word[st.session_state.fs_index]

    # 3. CSS Styling
    st.markdown("""
        <style>
        div[data-testid="stImage"] img {
            width: 100% !important;
            object-fit: contain !important;
            border-radius: 10px !important;
        }
        div[data-testid="stWebRtcStreamer"] {
            border-radius: 10px;
            overflow: hidden;
            border: 2px solid #ddd;
        }
        div.block-container {
            padding-top: 2rem !important; /* Reduced from default ~6rem */
            padding-bottom: 0rem !important;
            max-width: 95% !important; /* Optional: Use more screen width */
        }
        .current-letter { color: #007bff; font-weight: bold; font-size: 3.5rem; }
        .done-letter { color: #28a745; font-weight: normal; font-size: 3rem; }
        .future-letter { color: #ccc; font-weight: normal; font-size: 3rem; }
        </style>
    """, unsafe_allow_html=True)

    # 4. Back Button
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

    st.header(f"{get_string('fingerspelling_title', st.session_state.app_lang)} ({target_lang})")
    
    # col_left, col_video, col_instr = st.columns([1.2, 2.3, 2.5])
    col_left, col_video, col_instr = st.columns([1.5, 2.5, 2.0])
    
    # 5. Define Processor Factory
    # Captures 'current_target' from the local scope
    # Helper to get model-safe character
    model_target = current_target
    if target_lang == "ISL" and current_target in HEBREW_MAPPING:
        model_target = HEBREW_MAPPING[current_target]
    def processor_factory():
        try:
            return HandLandmarkProcessor(
                model=model,
                result_queue=current_queue,
                target_sign=model_target,
                language=target_lang,
                hold_sign_duration=0.3,
            )
        except Exception as e:
            print(f"FS Processor Error: {e}", flush=True)
            return None

    with col_left:
        if not st.session_state.fs_active:
            # --- INPUT MODE ---
            word_input = st.text_input(get_string("enter_word", st.session_state.app_lang))
            if st.button(get_string("start_practice", st.session_state.app_lang)):
                word = word_input.strip()
                valid = True
                if not word:
                    st.error("Please enter a word.")
                    valid = False
                elif " " in word:
                    st.error("Please enter a single word.")
                    valid = False
                else:
                    if target_lang == "ASL":
                        if not re.match(r"^[A-Za-z]+$", word):
                            st.error("ASL practice requires English letters.")
                            valid = False
                        else:
                            word = word.upper()
                    elif target_lang == "ISL":
                        if not re.match(r"^[\u0590-\u05FF]+$", word):
                            st.error("ISL practice requires Hebrew letters.")
                            valid = False
                
                if valid:
                    st.session_state.fs_word = word
                    st.session_state.fs_index = 0
                    st.session_state.fs_active = True
                    # Clear queue
                    while not st.session_state.result_queue.empty():
                        st.session_state.result_queue.get()
                    st.rerun()
        else:
            # --- ACTIVE MODE UI ---
            word = st.session_state.fs_word
            index = st.session_state.fs_index
            
            # Dynamic Word Display
            is_rtl = target_lang == "ISL"
            direction_style = "flex-direction: row-reverse;" if is_rtl else "flex-direction: row;"
            html = f"<div style='display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; {direction_style}'>"
            # Important: If RTL, we must iterate normally but the CSS handles visual order.
            # However, for the logic of coloring (past/present/future), the index remains 0->End.
            for i, char in enumerate(word):
                if i < index:
                    style = "color: #28a745; font-weight: bold; font-size: 2.5rem;" # Done
                elif i == index:
                    style = "color: #007bff; font-weight: bold; font-size: 3.5rem; text-decoration: underline;" # Current
                else:
                    style = "color: #ccc; font-weight: normal; font-size: 2.5rem;" # Future
                html += f"<span style='{style}'>{char}</span>"
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Manual Controls
            c_prev, c_next = st.columns(2)
            with c_prev:
                if st.button(get_string("prev_letter", st.session_state.app_lang), use_container_width=True):
                    if st.session_state.fs_index > 0:
                        st.session_state.fs_index -= 1
                        st.rerun()
            with c_next:
                 # "Skip" button
                 if st.button(get_string("next_letter", st.session_state.app_lang), use_container_width=True):
                    if st.session_state.fs_index < len(word):
                        st.session_state.fs_index += 1
                        if st.session_state.fs_index >= len(word):
                            st.session_state.fs_active = False
                            st.session_state.fs_success_trigger = True
                        st.rerun()
            
            st.markdown("---")
            if st.button("Stop / New Word", use_container_width=True):
                st.session_state.fs_active = False
                st.rerun()

    # 6. Video Column
    ctx = None
    with col_video:
        if st.session_state.fs_active and current_target:
            st.subheader(f"Current Target: {current_target}")
            
            if HAS_WEBRTC:
                # We use a static key so the camera DOES NOT reload between letters
                ctx = webrtc_streamer(
                    key="fingerspelling_cam",
                    mode=WebRtcMode.SENDRECV,
                    rtc_configuration={
                            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                        },
                    media_stream_constraints={
                        "video": {
                                # "width": {"min": 640, "ideal": 640, "max": 640},
                                # "height": {"min": 480, "ideal": 480, "max": 480},
                                "width": {"min": 480, "ideal": 480, "max": 480},
                                "height": {"min": 360, "ideal": 360, "max": 360},
                            "frameRate": {"max": 30},
                        },
                        "audio": False
                    },
                    video_processor_factory=processor_factory,
                    async_processing=True,
                    video_html_attrs={
                        "style": {"width": "100%", "border-radius": "10px"}, 
                        "controls": False, 
                        "autoPlay": True,
                        "playsInline": False,
                        "muted": True
                    },
                )
                
                # --- HOT SWAP LOGIC ---
                # This pushes the new letter to the running video processor
                if ctx.video_processor:
                    # Normalize again for the live update
                    live_target = current_target
                    if target_lang == "ISL" and current_target in HEBREW_MAPPING:
                        live_target = HEBREW_MAPPING[current_target]
                    ctx.video_processor.target_sign = live_target # <--- Send normalized
                    # ctx.video_processor.model = model
            else:
                st.error("WebRTC unavailable")
        
        elif not st.session_state.fs_active and st.session_state.get("fs_word"):
             # Completion State
             st.success(f"🎉 Word Completed: {st.session_state.fs_word}")
             if st.session_state.get("fs_success_trigger"):
                 st.balloons()
                 del st.session_state.fs_success_trigger
             
             if st.button("Practice Another Word"):
                 st.session_state.fs_word = ""
                 st.rerun()

    # 7. Instruction Column
    with col_instr:
        if st.session_state.fs_active and current_target:
            st.subheader("Hint")
            
            paths_to_try = [
                os.path.join("signing_instructions", f"{model_target}.png"),
                os.path.join("signing_instructions", f"{model_target.lower()}.png"),
                os.path.join("signing_instructions", f"{model_target.upper()}.png")
            ]
            
            found_img = None
            for p in paths_to_try:
                if os.path.exists(p):
                    found_img = p
                    break
            
            with st.container():
                if found_img:
                    st.image(found_img, use_container_width=True)
                    st.caption(f"How to sign: {current_target}")
                else:
                    st.info(f"No instruction image found for '{current_target}'")

    # 8. Background Polling (The Listener)
    # This runs independently to check for success messages from the video thread
    @st.fragment(run_every=0.2)
    def check_fs_success():
        try:           
            if not hasattr(st.session_state, "result_queue"):
                return
                
            msg = st.session_state.result_queue.get_nowait()
            
            if msg == "success":
                # Logic when user gets the sign right
                current_word_len = len(st.session_state.fs_word)
                
                # Advance index
                if st.session_state.fs_index < current_word_len:
                    st.session_state.fs_index += 1
                    
                    # Check if word is finished
                    if st.session_state.fs_index >= current_word_len:
                        st.session_state.fs_active = False
                        st.session_state.fs_success_trigger = True
                    
                    # Force UI update
                    st.rerun()
                    
        except queue.Empty:
            pass
            
    # Only run poller if active
    if st.session_state.fs_active:
        check_fs_success()