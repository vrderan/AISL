import streamlit as st
import os
import time
import queue
import traceback
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
    HAS_WEBRTC = True
except ImportError:
    HAS_WEBRTC = False

from streamlit_extras.stylable_container import stylable_container
from utils.localization import get_string
from utils.state import navigate_to, navigate_back, get_progress, increment_progress, decrement_progress, toggle_flag
from utils.data import get_category_signs, get_sign_display_name, get_sign_video_url, get_next_category
from utils.model_loader import load_model

@st.dialog("🎉 Category Mastered!")
def show_mastery_modal(category, target_lang):
    # Only fire balloons once per modal opening
    if not st.session_state.get("modal_balloons_fired", False):
        st.balloons()
        st.session_state.modal_balloons_fired = True
    
    next_cat = get_next_category(category, target_lang)
    
    # CASE 1: Next Category Available
    if next_cat:
        st.write(f"Amazing job! You have mastered all signs in **{target_lang} {category}**.")
        st.write("Ready for the next challenge?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Next: {target_lang} {next_cat}", type="primary", width='stretch'):
                st.session_state.category = next_cat
                st.session_state.current_sign = None 
                
                # Force video player rebuild
                if "video_key_id" not in st.session_state: st.session_state.video_key_id = 0
                st.session_state.video_key_id += 1 
                
                st.session_state.show_mastery_modal = False
                st.session_state.modal_balloons_fired = False # Reset for next time
                st.rerun()
        with col2:
            if st.button("Stay Here", width='stretch'):
                st.session_state.show_mastery_modal = False
                st.session_state.modal_balloons_fired = False
                st.rerun()

    # CASE 2: End of Course
    else:
        st.success(f"🏆 CONGRATULATIONS! You have mastered all available **{target_lang}** signs!")
        st.write("You are a legend. What would you like to do?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back to Menu", type="primary", width='stretch'):
                st.session_state.page = "language_selection"
                st.session_state.category = None
                st.session_state.show_mastery_modal = False
                st.session_state.modal_balloons_fired = False
                st.rerun()
        with col2:
            if st.button("Keep Practicing", width='stretch'):
                st.session_state.show_mastery_modal = False
                st.session_state.modal_balloons_fired = False
                st.rerun()

def render_learning():
    if "popover_counter" not in st.session_state:
        st.session_state.popover_counter = 0
    if "result_queue" not in st.session_state:
        st.session_state.result_queue = queue.Queue()
    
    st.markdown("""
        <style>
        /* Define TWO identical animations. 
           We switch between them to force the browser to replay the effect. */
        @keyframes flash-success-odd {
            0% { outline: 2px solid rgba(40, 167, 69, 0.8); outline-offset: 0px; }
            50% { outline: 8px solid rgba(40, 167, 69, 0); outline-offset: 6px; }
            100% { outline: 2px solid transparent; outline-offset: 15px; }
        }
        @keyframes flash-success-even {
            0% { outline: 2px solid rgba(40, 167, 69, 0.8); outline-offset: 0px; }
            50% { outline: 8px solid rgba(40, 167, 69, 0); outline-offset: 6px; }
            100% { outline: 2px solid transparent; outline-offset: 15px; }
        }
        
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

    st.markdown("""
        <style>
        div[data-testid="stPopoverBody"] button {
            background: transparent !important;
            color: inherit !important;
            border: 1px solid #ccc !important;
            box-shadow: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Check if the modal flag is set
    if st.session_state.get("show_mastery_modal", False):
        show_mastery_modal(st.session_state.category, st.session_state.target_lang)
    
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

    category = st.session_state.category
    target_lang = st.session_state.target_lang
    
    col_title, col_quiz = st.columns([3, 1])
    with col_title:
        st.markdown(f"""
                <h2 style="margin-bottom: 0.2rem; padding-bottom: 0.2rem; margin-top: 0rem; padding-top: 0rem;">
                    {get_string('learning_title', st.session_state.app_lang)}: {category} ({target_lang})
                </h2>
            """, unsafe_allow_html=True)
    with col_quiz:
        if st.button("🎓 Quiz Me!", use_container_width=True):
            # We don't change the category/lang, just the view
            navigate_to("quiz")
            st.rerun()
    
    col_list, col_video, col_instr = st.columns([1.5, 2.5, 2.0])
    
    signs = get_category_signs(category, target_lang)
    
    current_queue = st.session_state.result_queue
    current_sign = st.session_state.current_sign
    
    def processor_factory():
        try:
            from utils.video import HandLandmarkProcessor
            model = load_model(target_lang, category)
            return HandLandmarkProcessor(
                model=model,
                result_queue=current_queue,
                target_sign=current_sign,
                category=category,
                language=target_lang,
                translate_landmarks=True if category=='ABC' else False,
                scale_landmarks=True if category=='ABC' else False,
                hold_sign_duration = 0.75 if category=='ABC' else 0 if (target_lang=="ISL" and category=="Questions") else 0.1,
                success_cooldown = 2 if category=='ABC' else 2,
            )
        except Exception as e:
            print(f"CRITICAL VIDEO ERROR: {e}", flush=True)
            return None
    
    ctx = None

    with col_list:
        with st.container(height=700):
            for i, sign in enumerate(signs):
                if sign == "No Class":
                    continue
                    
                progress = get_progress(target_lang, category, sign)
                is_mastered = progress >= 3
                is_selected = st.session_state.current_sign == sign
                
                display_name = get_sign_display_name(sign, target_lang)
                label = f"{display_name} ({progress}/3)"
                if is_mastered: label = f"✅ {label}"
                
                key = f"sign_btn_{i}_{sign}"
                pct = int((progress / 3) * 100)
                if pct > 100: pct = 100
                
                base_bg = f"background: linear-gradient(to right, #e6ffe6 {pct}%, transparent {pct}%) !important;"
                
                # --- LOGIC SETUP ---
                last_success = st.session_state.get("last_success_sign", None)
                flash_counter = st.session_state.get("flash_counter", 0)
                should_flash = (sign == last_success)
                
                # --- KEY GENERATION ---
                # We use the INDEX (i) for the container key. 
                # This avoids all issues with Hebrew/Special characters in CSS class names.
                container_key = f"cont_btn_row_{i}"
                if should_flash:
                    # Append counter to force DOM rebuild
                    container_key += f"_{flash_counter}"
                
                # --- CSS GENERATION ---
                custom_class = "sign-btn"
                bg_color = f"linear-gradient(to right, #e6ffe6 {pct}%, transparent {pct}%)"
                border_color = "#b8bfc9"
                bottom_border = border_color # "#e0e0e0"
                text_color = "inherit"
                
                if is_selected:
                    bg_color = f"linear-gradient(to right, #d4edda {pct}%, #e6f2ff {pct}%)"
                    border_color = "#007bff"
                    bottom_border = "#007bff"
                    text_color = "#007bff"
                elif is_mastered:
                    bg_color = "#f0fff4"
                    border_color = "#28a745"
                    bottom_border = "#28a745"
                    text_color = "#155724"

                # --- ANIMATION SELECTION (The Fix) ---
                animation_css = ""
                if should_flash:
                    # Toggle between two identical animations to force browser replay
                    anim_name = "flash-success-odd" if flash_counter % 2 != 0 else "flash-success-even"
                    animation_css = f"animation: {anim_name} 1.0s ease-out !important; z-index: 2;"

                # --- RENDER CONTAINER ---
                c_row_btn, c_row_menu = st.columns([0.85, 0.15])
                
                with c_row_btn:
                    with st.container(key=container_key):
                        if st.button(label, key=key, width='stretch'):
                            st.session_state.current_sign = sign
                            st.rerun()

                # --- INJECT CSS ---
                st.markdown(f"""
                    <style>
                    .st-key-{container_key} button {{
                        border: 1px solid {border_color} !important;
                        border-bottom: 4px solid {bottom_border} !important;
                        background: {bg_color} !important;
                        color: {text_color} !important;
                        border-radius: 10px !important;
                        transition: transform 0.1s !important;
                        margin-bottom: -25px !important;
                        {animation_css}
                    }}
                    .st-key-{container_key} button:hover {{
                        border-color: {border_color} !important;
                        brightness: 95%;
                        transform: scale(1.01);
                    }}
                    </style>
                """, unsafe_allow_html=True)

                with c_row_menu:
                    popover_css = """
                        div[data-testid="stPopover"] > button {
                            border: none !important;
                            background: transparent !important;
                            padding: 0 !important;
                            color: inherit !important;
                            width: 100% !important;
                            display: flex !important;
                            justify-content: center !important;
                            align-items: center !important;
                        }
                        div[data-testid="stPopover"] > button > div > svg { display: none !important; }
                        div[data-testid="stPopover"] > button::after { display: none !important; }
                        div[data-testid='stPopover'] { margin-top: 7px; }
                    """
                    popover_dynamic_key = f"pop_{key}_{st.session_state.popover_counter}"
                    
                    with stylable_container(key=popover_dynamic_key, css_styles=popover_css):
                        with st.popover("⋮", width='stretch'):
                            if st.button(get_string("feedback_fail_detect", st.session_state.app_lang), key=f"fb_fail_{key}", width='stretch'):
                                st.session_state.popover_counter += 1
                                try:
                                    idx = signs.index(sign)
                                    next_sign = signs[idx+1] if idx + 1 < len(signs) else signs[0]
                                    if next_sign == "No Class":
                                        next_sign = signs[idx+2] if idx + 2 < len(signs) else signs[0]
                                    st.session_state.current_sign = next_sign
                                    st.session_state.feedback_message = {
                                        "type": "info",
                                        "text": f"Advancing: {get_sign_display_name(next_sign, target_lang)}"
                                    }
                                    st.rerun()
                                except ValueError: pass

                            if st.button(get_string("feedback_incorrect", st.session_state.app_lang), key=f"fb_inc_{key}", width='stretch'):
                                st.session_state.popover_counter += 1
                                decrement_progress(target_lang, category, sign)
                                st.session_state.feedback_message = {
                                    "type": "info",
                                    "text": get_string("feedback_thank_you", st.session_state.app_lang)
                                }
                                st.rerun()

                            if st.button(get_string("feedback_flag", st.session_state.app_lang), key=f"fb_flag_{key}", width='stretch'):
                                st.session_state.popover_counter += 1
                                toggle_flag(target_lang, category, sign)
                                st.session_state.feedback_message = {
                                    "type": "success",
                                    "text": get_string("flag_saved", st.session_state.app_lang)
                                }
                                st.rerun()
            
            if "feedback_message" in st.session_state:
                msg = st.session_state.feedback_message
                st.markdown("---") 
                if msg["type"] == "info":
                    st.info(msg["text"])
                elif msg["type"] == "success":
                    st.success(msg["text"])
                del st.session_state.feedback_message

    with col_video:
        if st.session_state.current_sign:
            current_sign_display = get_sign_display_name(st.session_state.current_sign, target_lang)
            st.markdown(f"""
                <h3 style="margin-bottom: 0px; padding-bottom: 0px;">
                    Sign: {current_sign_display}
                </h3>
            """, unsafe_allow_html=True)
            
            if HAS_WEBRTC:
                st.markdown(
                    """
                    <style>
                    div[data-testid="stWebRtcStreamer"] button {
                        display: none !important;
                        visibility: hidden !important;
                        height: 0px !important;
                    }
                    div[data-testid="stWebRtcStreamer"] > div {
                        gap: 0px !important;
                        padding: 0px !important;
                    }
                    video {
                        border-radius: 10px !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        display: block !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                key_id = st.session_state.get("video_key_id", 0)
                camera_key = f"camera_{key_id}"
                
                wrapper_css = """
                    div[data-testid="stWebRtcStreamer"] {
                        border: 5px solid transparent;
                        border-radius: 10px;
                        padding: 0.5rem !important;
                        transition: border-color 0.1s;
                    }
                """
                video_wrapper_key = "video_wrapper"
                
                with stylable_container(key=video_wrapper_key, css_styles=wrapper_css):
                    ctx = webrtc_streamer(
                        key=camera_key,
                        mode=WebRtcMode.SENDRECV,
                        media_stream_constraints={
                            "video": {
                                "width": {"min": 640, "ideal": 640, "max": 640},
                                "height": {"min": 480, "ideal": 480, "max": 480},
                                "frameRate": {"max": 30},
                            },
                            "audio": False
                        },
                        rtc_configuration={"iceServers": []},
                        video_processor_factory=processor_factory,
                        async_processing=True,
                        desired_playing_state=True,
                        video_html_attrs={
                            "style": {"width": "100%", "border-radius": "10px"}, 
                            "controls": False, 
                            "autoPlay": True,
                            "playsInline": False,
                            "muted": True
                        },
                    )
                
                if ctx.video_processor:
                    ctx.video_processor.target_sign = st.session_state.current_sign
                
                st.caption(get_string("disclaimer", st.session_state.app_lang))

            else:
                st.error("Missing streamlit-webrtc")
        
        else:
            st.subheader("Start Learning")
            st.markdown(
                """
                <div style="
                    height: 400px; 
                    background-color: #f8f9fa; 
                    border-radius: 10px; 
                    border: 2px dashed #ddd; 
                    display: flex; 
                    flex-direction: column;
                    align-items: center; 
                    justify-content: center; 
                    color: #aaa;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">👈</div>
                    <div>Select a sign from the list</div>
                    <div>to start learning</div>
                </div>
                """, 
                unsafe_allow_html=True
            )

    with col_instr:
        c_inst_title, c_inst_btn = st.columns([0.7, 0.3])
        with c_inst_title:
            st.subheader("Instructions")
        with c_inst_btn:
            if "show_instructions" not in st.session_state:
                st.session_state.show_instructions = True
            btn_label = "Hide" if st.session_state.show_instructions else "Show"
            
            with stylable_container(
                key="instr_btn_cont", 
                css_styles="""
                    div[data-testid="stButton"] > button { 
                        background: white !important; 
                        border: 1px solid #ccc !important;
                        color: #444 !important;
                        padding: 0.2rem 0.8rem !important;
                        font-size: 0.8rem !important;
                        min-height: 0px !important;
                        height: auto !important;
                        margin-top: 10px !important;
                        border-radius: 10px !important;
                    }
                    div[data-testid="stButton"] > button:hover {
                        background: #f9f9f9 !important;
                        border-color: #bbb !important;
                        color: #222 !important;
                    }
                """
            ):
                if st.button(btn_label, width='stretch'):
                    st.session_state.show_instructions = not st.session_state.show_instructions
                    st.rerun()

        with st.container():
            if st.session_state.get("show_instructions", True):
                try:
                    if st.session_state.current_sign:
                        if category == 'ABC':
                            local_img_path = os.path.join("images", f"{st.session_state.current_sign}.png")
                            if os.path.exists(local_img_path):
                                st.image(local_img_path, width='stretch')
                            else:
                                st.info(f"No instructions available for '{current_sign}'.")
                        else:
                            video_info = get_sign_video_url(current_sign, target_lang)
                            if video_info:
                                url, start_t, end_t = video_info
                                st.video(url, start_time=start_t, end_time=end_t, loop=False, muted=True, autoplay=True)
                            else:
                                st.info(f"No instructions available for '{current_sign}'.")
                        st.caption(f"How to sign: {current_sign_display}")
                    else:
                        st.markdown(
                            """
                            <div style="
                                padding: 1rem;
                                display: flex; 
                                align_items: center; 
                                justify_content: center; 
                                background-color: #f0f0f0; 
                                color: #888; 
                                border-radius: 10px;
                                text-align: center;">
                                <p style='margin:0;'>Select a sign to learn to view instructions</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                except Exception as e:
                    print(f"Instructions loading error:\n{traceback.format_exc()}", flush=True)
            else:
                st.markdown(
                    """
                    <div style="
                        padding: 1rem; 
                        display: flex; 
                        align_items: center; 
                        justify_content: center; 
                        background-color: #f0f0f0; 
                        color: #888; 
                        border-radius: 10px;">
                        <p style='margin:0;'>Instructions Hidden</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    
    @st.fragment(run_every=0.3)
    def check_for_success():
        # If we are not on the learning page, stop immediately.
        # This prevents the "Fragment does not exist" spam in your logs.
        if st.session_state.get("page") != "learning":
            return
        if st.session_state.get("show_mastery_modal", False):
            return
        
        try:            
            if not hasattr(st.session_state, "result_queue"):
                return
            msg = st.session_state.result_queue.get_nowait()
            
            if msg == "success":
                st.session_state.last_success_sign = st.session_state.current_sign
                increment_progress(target_lang, category, st.session_state.current_sign)
                # st.session_state.flash_time = time.time()
                if "flash_counter" not in st.session_state:
                    st.session_state.flash_counter = 0
                st.session_state.flash_counter += 1
                
                new_progress = get_progress(target_lang, category, st.session_state.current_sign)
                
                if new_progress >= 3:
                    st.session_state.flash_type = "complete"
                    idx = signs.index(st.session_state.current_sign)
                    next_sign = signs[idx+1] if idx + 1 < len(signs) else signs[0]
                    st.session_state.current_sign = next_sign
                    st.session_state.feedback_message = {
                        "type": "success", 
                        "text": f"Mastered! Advancing to: {get_sign_display_name(next_sign, target_lang)}"
                    }
                else:
                    st.session_state.flash_type = "standard"
                    st.session_state.feedback_message = {
                        "type": "success", 
                        "text": get_string("success_msg", st.session_state.app_lang)
                    }
                
                if ctx and ctx.video_processor:
                    ctx.video_processor.target_sign = st.session_state.current_sign

                # Check if every single sign in the list is now mastered (>= 3)
                all_mastered = all(get_progress(target_lang, category, s) >= 3 for s in signs)
                
                # We use a specific key to ensure we don't re-trigger this if they choose "Stay Here"
                # The 'celebrated' flag resets only when category changes.
                celebration_key = f"celebrated_{target_lang}_{category}"
                already_celebrated = st.session_state.get(celebration_key, False)

                if all_mastered and not already_celebrated:
                    # 1. Mark as celebrated so we don't loop
                    st.session_state[celebration_key] = True
                    
                    # 2. Trigger the modal flag
                    st.session_state.show_mastery_modal = True
                    
                    # 3. Optional: Initial Celebration before modal opens
                    st.toast(f"🎉 CONGRATULATIONS! You have mastered the '{category}' category!")
                    time.sleep(1.0) # Short pause before the reruns opens the modal
                
                st.rerun()

        except queue.Empty:
            pass
            
    check_for_success()