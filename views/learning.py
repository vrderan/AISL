import streamlit as st
import os
import time
import queue
import traceback
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
    HAS_WEBRTC = True
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    HAS_WEBRTC = False
    st_autorefresh = None

from streamlit_extras.stylable_container import stylable_container
from utils.localization import get_string
from utils.state import navigate_to, navigate_back, get_progress, increment_progress, decrement_progress, toggle_flag
from utils.data import get_category_signs, get_sign_display_name, get_sign_video_url, get_next_category
from utils.video import HandLandmarkProcessor
from utils.model_loader import load_model

# @st.dialog("🎉 Category Mastered!")
# def show_mastery_modal(category, target_lang):
#     print('showing mastery modal')
#     # Only fire once per modal opening
#     if not st.session_state.get("modal_balloons_fired", False):
#         st.balloons()
#         st.session_state.modal_balloons_fired = True
    
#     next_cat = get_next_category(category)
    
#     # CASE 1: Next Category Available
#     if next_cat:
#         st.write(f"Amazing job! You have mastered all signs in **{category}**.")
#         st.write("Ready for the next challenge?")
        
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button(f"Next: {next_cat}", type="primary", use_container_width=True):
#                 st.session_state.category = next_cat
#                 st.session_state.current_sign = None 
                
#                 # NUCLEAR OPTION: Force video player to destroy and rebuild
#                 if "video_key_id" not in st.session_state: st.session_state.video_key_id = 0
#                 st.session_state.video_key_id += 1 
                
#                 st.session_state.show_mastery_modal = False
#                 st.rerun()
#         with col2:
#             if st.button("Stay Here", use_container_width=True):
#                 st.session_state.show_mastery_modal = False
#                 st.rerun()

#     # CASE 2: End of Course
#     else:
#         st.success(f"🏆 CONGRATULATIONS! You have mastered all available **{target_lang}** signs!")
#         st.write("You are a legend. What would you like to do?")
        
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("Back to Menu", type="primary", use_container_width=True):
#                 st.session_state.page = "language_selection"
#                 st.session_state.category = None
#                 st.session_state.show_mastery_modal = False
#                 st.rerun()
#         with col2:
#             if st.button("Keep Practicing", use_container_width=True):
#                 st.session_state.show_mastery_modal = False
#                 st.rerun()

def render_learning():
    if "popover_counter" not in st.session_state:
        st.session_state.popover_counter = 0
    if "pulse_id" not in st.session_state:
        st.session_state.pulse_id = 0
    if "result_queue" not in st.session_state:
        st.session_state.result_queue = queue.Queue()
    
    st.markdown("""
        <style>
        @keyframes flash-green-border {
            0% { border-color: transparent; box-shadow: 0 0 0 0 transparent; }
            50% { border-color: #28a745; box-shadow: 0 0 20px 5px #28a745; }
            100% { border-color: transparent; box-shadow: 0 0 0 0 transparent; }
        }
        @keyframes flash-gold-border {
            0% { border-color: transparent; box-shadow: 0 0 0 0 transparent; }
            50% { border-color: #FFD700; box-shadow: 0 0 20px 5px #FFD700; }
            100% { border-color: transparent; box-shadow: 0 0 0 0 transparent; }
        }
        @keyframes subtle-pulse {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
            50% { transform: scale(1.05); box-shadow: 0 0 20px 10px rgba(40, 167, 69, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
        }
        div.block-container {
            padding-top: 1rem !important; /* Reduced from default ~6rem */
            padding-bottom: 0rem !important;
            max-width: 95% !important; /* Optional: Use more screen width */
        }
        
        # /* Optional: Hide the top header decoration bar if you want it flush */
        # header {
        #     visibility: hidden;
        # }
        /* Fix for instruction image sizing and rounding */
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

    # # If the flag is True, Streamlit halts and overlays the dialog.
    # if st.session_state.get("show_mastery_modal", False):
    #     show_mastery_modal(st.session_state.category, st.session_state.target_lang)
    
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
            print('back button pressed')
            navigate_back()
            st.rerun()

    category = st.session_state.category
    target_lang = st.session_state.target_lang
    
    # st.header(f"{get_string('learning_title', st.session_state.app_lang)}: {category} ({target_lang})")
    st.markdown(f"""
                <h2 style="margin-bottom: 0.2rem; padding-bottom: 0.2rem; margin-top: 0rem; padding-top: 0rem;">
                    {get_string('learning_title', st.session_state.app_lang)}: {category} ({target_lang})
                </h2>
            """, unsafe_allow_html=True)
    
    col_list, col_video, col_instr = st.columns([1.5, 2.5, 2.0])
    
    signs = get_category_signs(category, target_lang)
    # print(f'loaded signs: {signs}')
    
    # Load Model
    print(f"Loading model for {target_lang} {category}")
    model = load_model(target_lang, category)
    # print(f'loaded signs: {signs}')
    
    # We do this HERE so the values are ready for the background thread
    current_queue = st.session_state.result_queue
    current_sign = st.session_state.current_sign
    
    def processor_factory():
        try:
            return HandLandmarkProcessor(
                model=model,
                result_queue=current_queue,
                target_sign=current_sign,
                category=category,
                language=target_lang,
                translate_landmarks=True if category=='ABC' else False,
                scale_landmarks=True if category=='ABC' else False,
                hold_sign_duration = 1 if category=='ABC' else 0.33,
                success_cooldown = 2 if category=='ABC' else 3,
            )
        except Exception as e:
            print(f"CRITICAL VIDEO ERROR: {e}", flush=True)
            return None
    
    # Determine if flash is active
    flash_active = True
    # if "flash_time" in st.session_state:
    #     if time.time() - st.session_state.flash_time < 2.0: # 2 seconds window
    #         flash_active = True
    
    ctx = None

    with col_list:
        # st.caption("Select a sign to learn")
        with st.container(height=700):
            print(f'st.session_state.current_sign: {st.session_state.current_sign}')
            # print(f'loaded signs: {signs}')
            for i, sign in enumerate(signs):
                if sign == "No Class":
                    continue
                progress = get_progress(target_lang, category, sign)
                is_mastered = progress >= 3
                is_selected = st.session_state.current_sign == sign
                # print(f'sign "{sign}" is selected: {is_selected}')
                
                display_name = get_sign_display_name(sign, target_lang)
                label = f"{display_name} ({progress}/3)"
                if is_mastered: label = f"✅ {label}"
                
                key = f"sign_btn_{i}_{sign}"
                
                pct = int((progress / 3) * 100)
                if pct > 100: pct = 100
                
                base_bg = f"background: linear-gradient(to right, #e6ffe6 {pct}%, transparent {pct}%) !important;"
                
                base_css = f"""
                    button {{
                        width: 100% !important;
                        border-radius: 10px !important;
                        border: none !important;
                        border-bottom: 3px solid #e0e0e0 !important;
                        {base_bg}
                        text-align: left !important;
                        padding-left: 1rem !important;
                        color: inherit !important; 
                        animation: none !important;
                    }}
                    button:hover {{ 
                        background: linear-gradient(to right, #e6ffe6 {pct}%, rgba(128, 128, 128, 0.1) {pct}%) !important; 
                    }}
                """
                
                if is_selected:
                    row_css = f"""
                    button {{
                        width: 100% !important;
                        border-radius: 10px !important;
                        border: none !important;
                        border-bottom: 3px solid #007bff !important;
                        background: linear-gradient(to right, #d4edda {pct}%, #e6f2ff {pct}%) !important;
                        color: #007bff !important;
                        text-align: left !important;
                        padding-left: 1rem !important;
                        font-weight: bold !important;
                    }}
                    button:hover {{ background: linear-gradient(to right, #c3e6cb {pct}%, #d0e4ff {pct}%) !important; }}
                    """
                elif is_mastered:
                    row_css = """
                    button {
                        width: 100% !important;
                        border-radius: 10px !important;
                        border: none !important;
                        border-bottom: 3px solid #28a745 !important;
                        background: #e6ffe6 !important;
                        color: #155724 !important;
                        text-align: left !important;
                        padding-left: 1rem !important;
                    }
                    button:hover { background: #d4edda !important; }
                    """
                else:
                    row_css = base_css
                
                # Apply Pulse Animation
                pulse_id = st.session_state.get("pulse_id", 0)
                cont_key = f"cont_{key}"
                
                # if flash_active and is_selected:#st.session_state.get("last_success_sign") == sign:
                if is_selected:
                    print(f'added animation to sign: {sign}')
                    # UPDATED CSS:
                    # 1. We use '> button' to ensure we only target the direct button child, not nested ones.
                    # 2. We removed the static 'box-shadow' line (the fallback), which was causing the persistent border.
                    # 3. We use '!important' on the animation to force it over default styles.
                    row_css += """
                        div[data-testid="stButton"] > button {
                            animation: subtle-pulse 1s ease-out !important;
                            z-index: 2 !important;
                            position: relative !important;
                            /* REMOVED THE STATIC BOX-SHADOW LINE HERE */
                        }
                    """
                    cont_key = f"cont_{key}_{pulse_id}"
                # else:
                #     print(f'sign "{sign}" should not have an animation')

                c_row_btn, c_row_menu = st.columns([0.85, 0.15])
                with c_row_btn:
                     with stylable_container(key=cont_key, css_styles=row_css):
                        if st.button(label, key=key, use_container_width=True):
                            st.session_state.current_sign = sign
                            print(f'{sign} button pressed')
                            st.rerun()

                with c_row_menu:
                    popover_css = """
                        /* Reset button styles */
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
                        
                        /* Hide the SVG arrow icon */
                        div[data-testid="stPopover"] > button > div > svg {
                            display: none !important;
                        }
                        
                        /* Hide pseudo-elements just in case */
                        div[data-testid="stPopover"] > button::after {
                            display: none !important;
                        }
                        div[data-testid='stPopover'] { margin-top: 7px;
                        }
                    """
                    popover_dynamic_key = f"pop_{key}_{st.session_state.popover_counter}"
                    
                    with stylable_container(key=popover_dynamic_key, css_styles=popover_css):
                        with st.popover("⋮", use_container_width=True):
                            if st.button(get_string("feedback_fail_detect", st.session_state.app_lang), key=f"fb_fail_{key}", use_container_width=True):
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
                                    st.toast(f"Skipped: {display_name}")
                                    print('feedback_fail_detect button pressed')
                                    st.rerun()
                                except ValueError: pass

                            if st.button(get_string("feedback_incorrect", st.session_state.app_lang), key=f"fb_inc_{key}", use_container_width=True):
                                st.session_state.popover_counter += 1
                                decrement_progress(target_lang, category, sign)
                                st.session_state.feedback_message = {
                                    "type": "info",
                                    "text": get_string("feedback_thank_you", st.session_state.app_lang)
                                }
                                st.toast(get_string("feedback_thank_you", st.session_state.app_lang))
                                print('feedback_incorrect button pressed')
                                st.rerun()

                            if st.button(get_string("feedback_flag", st.session_state.app_lang), key=f"fb_flag_{key}", use_container_width=True):
                                st.session_state.popover_counter += 1
                                toggle_flag(target_lang, category, sign)
                                st.session_state.feedback_message = {
                                    "type": "success",
                                    "text": get_string("flag_saved", st.session_state.app_lang)
                                }
                                st.toast(get_string("flag_saved", st.session_state.app_lang))
                                print('feedback_flag button pressed')
                                st.rerun()
            
            if "feedback_message" in st.session_state:
                msg = st.session_state.feedback_message
                st.markdown("---") 
                if msg["type"] == "info":
                    st.info(msg["text"])
                elif msg["type"] == "success":
                    st.success(msg["text"])
                del st.session_state.feedback_message

        # st.markdown("---")
        # if st.button(get_string("simulate_success", st.session_state.app_lang), use_container_width=True):
        #     st.session_state.last_success_sign = st.session_state.current_sign
        #     increment_progress(target_lang, category, st.session_state.current_sign)
        #     new_progress = get_progress(target_lang, category, st.session_state.current_sign)
            
        #     # Set timestamp for flash
        #     st.session_state.flash_time = time.time()
        #     # Increment pulse_id to force DOM recreation for animation replay
        #     st.session_state.pulse_id += 1
            
        #     if new_progress >= 3:
        #         st.session_state.flash_type = "complete"
        #         idx = signs.index(st.session_state.current_sign)
        #         next_sign = signs[idx+1] if idx + 1 < len(signs) else signs[0]
        #         st.session_state.current_sign = next_sign
        #         st.session_state.feedback_message = {"type": "success", "text": f"Advancing: {get_sign_display_name(next_sign, target_lang)}"}
        #     else:
        #         st.session_state.flash_type = "standard"
        #         st.session_state.feedback_message = {"type": "success", "text": get_string("success_msg", st.session_state.app_lang)}
                
        #     # Check if every single sign in the list is now mastered (>= 3)
        #     all_mastered = all(get_progress(target_lang, category, s) >= 3 for s in signs)
        #     if all_mastered:
        #         print("Category Mastered!")
        #         st.session_state.has_celebrated = True # Stop future loops
        #         st.balloons()
        #         st.toast(f"🎉 CONGRATULATIONS! You have mastered the '{category}' category!")
        #         # PAUSE HERE: Let the balloons fly for 3 seconds before reloading
        #         time.sleep(2)
            
        #     print('simulate_success button pressed')
        #     st.rerun()

    with col_video:
        if st.session_state.current_sign:
            current_sign_display = get_sign_display_name(st.session_state.current_sign, target_lang)
            # st.subheader(f"Sign: {current_sign_display}")
            # st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
            # Use HTML directly for the subheader to have full control over margins
            st.markdown(f"""
                <h3 style="margin-bottom: 0px; padding-bottom: 0px;">
                    Sign: {current_sign_display}
                </h3>
            """, unsafe_allow_html=True)
            
            if HAS_WEBRTC:
                st.markdown(
                    """
                    <style>
                    /* 1. HIDE ALL BUTTONS inside the WebRTC component (Start, Stop, Select Device) */
                    div[data-testid="stWebRtcStreamer"] button {
                        display: none !important;
                        visibility: hidden !important;
                        height: 0px !important;
                    }
                    
                    /* 2. REMOVE THE WHITE FRAME (Internal Padding) */
                    /* This targets the flex container holding the video and controls */
                    div[data-testid="stWebRtcStreamer"] > div {
                        gap: 0px !important;
                        padding: 0px !important;
                    }
                    
                    /* 3. Force Video to be full width/height without gaps */
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

                # if flash_active:
                #     f_type = st.session_state.get("flash_type", "standard")
                #     # Incrementing the key to force animation replay
                #     video_wrapper_key = f"video_wrapper_{st.session_state.pulse_id}"
                    
                #     if f_type == "complete":
                #          wrapper_css = """
                #             div[data-testid="stWebRtcStreamer"] {
                #                 border: 5px solid #FFD700 !important;
                #                 border-radius: 10px;
                #                 box-shadow: 0 0 20px 5px #FFD700;
                #                 animation: flash-gold-border 1s;
                #             }
                #         """
                #     else:
                #         wrapper_css = """
                #             div[data-testid="stWebRtcStreamer"] {
                #                 border: 5px solid #28a745 !important;
                #                 border-radius: 10px;
                #                 box-shadow: 0 0 20px 5px #28a745;
                #                 animation: flash-green-border 0.5s;
                #             }
                #         """
                
                with stylable_container(key=video_wrapper_key, css_styles=wrapper_css):
                    ctx = webrtc_streamer(
                        key=camera_key,
                        mode=WebRtcMode.SENDRECV,
                        # rtc_configuration={
                        #     "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                        # },
                        media_stream_constraints={
                            "video": {
                                "width": {"min": 640, "ideal": 640, "max": 640},
                                "height": {"min": 480, "ideal": 480, "max": 480},
                                # "width": {"min": 480, "ideal": 480, "max": 480},
                                # "height": {"min": 360, "ideal": 360, "max": 360},
                                "frameRate": {"max": 30},
                            },
                            "audio": False
                        },
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
                    # This is the magic. We update the attribute on the LIVE object.
                    # No restart required.
                    ctx.video_processor.target_sign = st.session_state.current_sign
                    
                    # # Optional: Update the model if the language changed 
                    # # (Only needed if you support switching languages mid-stream)
                    # ctx.video_processor.model = model
                
                st.caption(get_string("disclaimer", st.session_state.app_lang))

            else:
                st.error("Missing streamlit-webrtc")
        
        else:
            # --- NEW EMPTY STATE ---
            st.subheader("Start Learning")
            
            # Placeholder box to keep layout stable
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
        # Create a mini 2-column layout: Text (Left) | Button (Right)
        c_inst_title, c_inst_btn = st.columns([0.7, 0.3])
        
        with c_inst_title:
            st.subheader("Instructions")
            
        with c_inst_btn:
            # Check state
            if "show_instructions" not in st.session_state:
                st.session_state.show_instructions = True
            
            # Simple "Show" / "Hide" text
            btn_label = "Hide" if st.session_state.show_instructions else "Show"
            
            # Compact button style aligned with the header
            with stylable_container(
                key="instr_btn_cont", 
                css_styles="""
                    button { 
                        background: white !important; 
                        border: 1px solid #ccc !important; /* Thin grey border */
                        color: #444 !important; /* Dark gray text */
                        padding: 0.2rem 0.8rem !important;
                        font-size: 0.8rem !important;
                        min-height: 0px !important;
                        height: auto !important;
                        margin-top: 10px !important;
                        border-radius: 10px !important;
                    }
                    button:hover {
                        background: #f9f9f9 !important;
                        border-color: #bbb !important;
                    }
                """
            ):
                if st.button(btn_label, use_container_width=True):
                    st.session_state.show_instructions = not st.session_state.show_instructions
                    print('instructions button pressed')
                    st.rerun()

        # Removed fixed height container
        with st.container():
            # Check if instructions are enabled
            if st.session_state.get("show_instructions", True):
                try:
                    if st.session_state.current_sign:
                        if category == 'ABC':
                            # Check for local image
                            #  local_img_path = f"signing_instructions/{st.session_state.current_sign}.png"
                            local_img_path = os.path.join("signing_instructions", f"{st.session_state.current_sign}.png")
                            if os.path.exists(local_img_path):
                                st.image(local_img_path, use_container_width=True)
                            else:
                                # st.info(f"No image available for {st.session_state.current_sign}. Please add '{st.session_state.current_sign}.png' to 'signing_instructions' folder.")
                                st.info(f"No instructions available for '{current_sign}'.")
                        else:
                            video_info = get_sign_video_url(current_sign, target_lang)
                            if video_info:
                                url, start_t = video_info
                                # Display YouTube Video
                                print('showing instructions video')
                                st.video(url, start_time=start_t, muted=True, autoplay=True)
                            else:
                                st.info(f"No instructions available for '{current_sign}'.")
                        
                        st.caption(f"How to sign: {current_sign_display}")
                    else:
                        # Default message when instructions are ON but no sign selected
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
                # Message when instructions are HIDDEN
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
    
    
    # --- NEW POLLING LOGIC ---
    # @st.fragment isolates this function so it reruns independently.
    # run_every=0.2 tells it to run this specific function every 0.2 seconds.
    # The rest of the app does NOT rerun, so buttons remain clickable!
    @st.fragment(run_every=0.2)
    def check_for_success():
        # 1. ZOMBIE CHECK (Page Navigation)
        if st.session_state.page != "learning":
            return
            
        # 2. MODAL CHECK (Stop processing if modal is open)
        # This fixes the infinite loop/balloon spam
        if st.session_state.get("show_mastery_modal", False):
            return
        
        try:            
            # Check the queue without blocking
            if not hasattr(st.session_state, "result_queue"):
                return
                
            msg = st.session_state.result_queue.get_nowait()
            
            if msg == "success":
                # --- SUCCESS LOGIC (Only runs when success actually happens) ---
                
                # Update Session State
                st.session_state.last_success_sign = st.session_state.current_sign
                increment_progress(target_lang, category, st.session_state.current_sign)
                
                st.session_state.flash_time = time.time()
                st.session_state.pulse_id += 1
                
                # Check for Level Completion / Next Sign
                new_progress = get_progress(target_lang, category, st.session_state.current_sign)
                
                if new_progress >= 3:
                    st.session_state.flash_type = "complete"
                    
                    # Advance to next sign
                    # Note: We access 'signs' from the outer scope, which is fine
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
                
                # Update the Live Processor (Hot Swap)
                # We need to reach into the global 'ctx' variable
                if ctx and ctx.video_processor:
                    ctx.video_processor.target_sign = st.session_state.current_sign

                # Check if every single sign in the list is now mastered (>= 3)
                # print(f'signs: {signs}')
                all_mastered = all(get_progress(target_lang, category, s) >= 3 for s in signs)
                
                # # Check if we already celebrated this specific category to avoid spam
                # celebration_key = f"celebrated_{target_lang}_{category}"
                # already_celebrated = st.session_state.get(celebration_key, False)
                # print(f'already_celebrated: {already_celebrated}')
                # if all_mastered and not already_celebrated:
                #     print("Category Mastered!")
                #     st.session_state.show_mastery_modal = True
                #     st.session_state[celebration_key] = True
                
                # Check if we already celebrated this specific category to avoid spam
                if all_mastered:
                    print("Category Mastered!")
                    st.balloons()
                    st.toast(f"🎉 CONGRATULATIONS! You have mastered the '{category}' category!")
                    # PAUSE HERE: Let the balloons fly for 3 seconds before reloading
                    time.sleep(2)
                
                # Trigger FULL App Rerun
                # We only do this ONCE upon success, so the UI updates to show the new sign
                st.rerun()

        except queue.Empty:
            pass # Do nothing, app stays idle
            
    # Call the fragment function
    check_for_success()