import cv2
import av
import time
import numpy as np
from typing import List, Dict, Any
import traceback
from PIL import Image, ImageDraw, ImageFont
import platform
import random
from bidi.algorithm import get_display
import torch
import math

try:
    import mediapipe as mp
    from streamlit_webrtc import VideoProcessorBase
    HAS_WEBRTC = True
except ImportError:
    HAS_WEBRTC = False
    VideoProcessorBase = object

if HAS_WEBRTC:
    class HandLandmarkProcessor(VideoProcessorBase):
        def __init__(self,
                     model=None, # the model used for classification
                     result_queue=None, # the queue to pass back to the app
                     target_sign=None, # the current objective sign
                     category=None, # the current category of signs
                     language='ASL', # the current objective sign language
                     static_image_mode: bool = True,
                     max_num_hands: int = 2,
                     min_detection_confidence: float = 0.5,
                     min_tracking_confidence: float = 0.5,
                     translate_landmarks: bool = True, # wether to translate the detected hand landmarks relative to wrist
                     scale_landmarks: bool = True, # wether to scale the size of the detected hand landmarks
                     rotate_landmarks: bool = False, # wether to upright the detected hand landmarks
                     hold_sign_duration: float = 1, # the time the user needs to hold correct sign before success
                     success_cooldown: float = 2.0, # the time the app waits before allowing next attempt
                     sequence_length: int = 15 # the length of the LSTM window
                     ):
            
            # self.frame_count = 0
            # self.start_time = time.time()
            
            # if category == 'ABC':
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(static_image_mode=static_image_mode,
                                            max_num_hands=max_num_hands,
                                            min_detection_confidence=min_detection_confidence,
                                            min_tracking_confidence=min_tracking_confidence,
                                            model_complexity=0,  # 0 = Lite (Fastest), 1 = Full (Default)
                                            )
            # else:
            #     self.mp_hands = mp.solutions.holistic
            #     self.hands = self.mp_hands.Holistic(static_image_mode=static_image_mode,
            #                                         min_detection_confidence=min_detection_confidence,
            #                                         min_tracking_confidence=min_tracking_confidence,
            #                                         )
                
            self.mp_styles = mp.solutions.drawing_styles
            # self.landmark_style, self.connection_style = self.get_fun_hand_styles()
            self.landmark_style = self.mp_styles.get_default_hand_landmarks_style()
            self.connection_style = self.mp_styles.get_default_hand_connections_style()
            self.mp_drawing = mp.solutions.drawing_utils
            self.init_frame_thickness = 10
            
            self.translate_landmarks = translate_landmarks
            self.scale_landmarks = scale_landmarks
            self.rotate_landmarks = rotate_landmarks
            self.model = model
            self.model_classes = list(model.classes_) if model else []
            # print(f"Model classes: {self.model_classes}")
            self.result_queue = result_queue
            self.target_sign = target_sign
            self.category = category
            self.language = language
            self.previous_target_sign = target_sign
            self.first_match_time = None
            self.last_match_time = None
            self.current_holding = 0
            self.hold_sign_duration = hold_sign_duration
            self.in_cooldown = False
            self.success_cooldown = success_cooldown # Cooldown to prevent spam
            self.success_messages = ['SUCCESS!', 'Good Job!', 'Amazing!', 'Great! Keep Going!'] if language == 'ASL' else ['כל הכבוד!', 'עבודה טובה!', 'מעולה!', 'ככה עושים את זה!']
            self.success_msg = random.choice(self.success_messages)
            self.hold_msg = 'Hold...' if language == 'ASL' else 'לא לזוז...'
            self.reset_msg = "Reset Hand and Try Again" if language == 'ASL' else 'נא לאפס תנוחת יד ולנסות שוב'
            self.reset_hand = True

            # LSTM BUFFER VARIABLES
            self.sequence_buffer = [] 
            self.sequence_length = sequence_length
            self.prediction_threshold = 0.75 # Confidence required to trigger dynamic sign

        # not used
        def get_fun_hand_styles(self):
            """
            Returns a custom, colorful styling dictionary for hand landmarks 
            and a clean style for connections.
            """
            mp_drawing = mp.solutions.drawing_utils
            
            # --- PALETTE (BGR) ---
            # "Pastel Pop" colors
            c_wrist  = (240, 240, 240) # Off-white
            c_thumb  = (128, 128, 255) # Pastel Red/Pink
            c_index  = (255, 191, 0)   # Deep Sky Blue
            c_middle = (0, 255, 127)   # Spring Green
            c_ring   = (255, 105, 180) # Hot Pink
            c_pinky  = (0, 165, 255)   # Orange
            
            # Dimensions
            radius = 4
            thickness = 2
            
            # --- LANDMARKS (Dictionary Mapping) ---
            landmark_style = {}
            
            # 0: Wrist
            landmark_style[0] = mp_drawing.DrawingSpec(color=c_wrist, thickness=thickness, circle_radius=radius)
            
            # 1-4: Thumb
            for i in range(1, 5):
                landmark_style[i] = mp_drawing.DrawingSpec(color=c_thumb, thickness=thickness, circle_radius=radius)
                
            # 5-8: Index
            for i in range(5, 9):
                landmark_style[i] = mp_drawing.DrawingSpec(color=c_index, thickness=thickness, circle_radius=radius)
                
            # 9-12: Middle
            for i in range(9, 13):
                landmark_style[i] = mp_drawing.DrawingSpec(color=c_middle, thickness=thickness, circle_radius=radius)
                
            # 13-16: Ring
            for i in range(13, 17):
                landmark_style[i] = mp_drawing.DrawingSpec(color=c_ring, thickness=thickness, circle_radius=radius)
                
            # 17-20: Pinky
            for i in range(17, 21):
                landmark_style[i] = mp_drawing.DrawingSpec(color=c_pinky, thickness=thickness, circle_radius=radius)

            # --- CONNECTIONS (Single Spec) ---
            # Clean white lines to let the dots pop
            connection_style = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
            
            return landmark_style, connection_style
        
        def draw_modern_text(self, img, text, y_pos=50, font_size=40, color=(255, 255, 255), centered=True):
            """
            Draws text with Hebrew/BiDi support and automatic font fallback.
            """
            # 1. Convert to PIL
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)

            # 2. Hebrew Logic (Fix Direction)
            if self.language == "ISL" or any("\u0590" <= c <= "\u05ea" for c in text):
                text = get_display(text)

            # 3. Load Font (Loop through options until one works)
            # We prioritize Arial because it is the safest bet for Hebrew on Windows.
            font_options = [
                # Windows
                "arial.ttf", 
                "seguiemj.ttf", 
                "segoeui.ttf", 
                "david.ttf", 
                # Mac
                "Arial.ttf", 
                "HelveticaNeue.ttc",
                # Linux / Streamlit Cloud
                "DejaVuSans.ttf", 
                "FreeSans.ttf"
            ]
            
            # Dynamic font size and stroke thickness based on width (Reference: 640px)
            scale_ratio = img_pil.width / 640.0
            dynamic_stroke = max(1, int(3 * scale_ratio))
            dynamic_font_size = int(scale_ratio * font_size)
            
            font = None
            for f_name in font_options:
                try:
                    # Try to load the font
                    font = ImageFont.truetype(f_name, dynamic_font_size)
                    # If successful, break the loop
                    break 
                except IOError:
                    continue
            
            # If ALL fonts fail, load default (this will show squares for Hebrew, but it's a last resort)
            if font is None:
                print("WARNING: No TrueType font found. Hebrew will likely fail.")
                font = ImageFont.load_default()

            # 4. Calculate Size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            
            if centered:
                x = (img_pil.width - text_width) // 2
            else:
                x = 20

            # 5. Draw with Outline
            rgb_color = (color[0], color[1], color[2])
            outline_color = (0, 0, 0)
            
            draw.text(
                (x, y_pos), 
                text, 
                font=font, 
                fill=rgb_color, 
                stroke_width=dynamic_stroke, 
                stroke_fill=outline_color
            )
            
            return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        def normalize_hand_landmarks(self, landmarks: np.ndarray) -> np.ndarray:
            """
            Normalize hand landmarks for scale, translation, and in-plane rotation.

            Parameters
            ----------
            landmarks : np.ndarray
                Shape (21, 3), MediaPipe landmark order.

            Returns
            -------
            np.ndarray
                Normalized landmarks, shape (21, 3)
            """
            landmarks = landmarks.copy()

            # ---- 1. Translation normalization (wrist as origin) ----
            if self.translate_landmarks:
                wrist = landmarks[0]
                landmarks -= wrist

            # ---- 2. Scale normalization (palm size) ----
            # Use distance wrist -> middle MCP (index 9) as scale reference
            if self.scale_landmarks:
                palm_size = np.linalg.norm(landmarks[9])
                if palm_size > 0:
                    landmarks /= palm_size

            # ---- 3. Rotation normalization (align wrist->index MCP to x-axis) ----
            if self.rotate_landmarks:
                index_mcp = landmarks[5]  # index finger MCP
                angle = np.arctan2(index_mcp[1], index_mcp[0])

                rotation_matrix = np.array(
                    [
                        [np.cos(-angle), -np.sin(-angle), 0.0],
                        [np.sin(-angle),  np.cos(-angle), 0.0],
                        [0.0,             0.0,            1.0],
                    ],
                    dtype=np.float32,
                )

                landmarks = landmarks @ rotation_matrix.T

            return landmarks
        
        def process_image(self, rgb_image: np.ndarray) -> List[Dict[str, Any]]:
            """
            Main entry point.

            Parameters
            ----------
            rgb_image : np.ndarray
                RGB image (H, W, 3), uint8 or float.

            Returns
            -------
            List[Dict]
                One dict per detected hand:
                {
                    "handedness": "Left" | "Right",
                    "raw_landmarks": np.ndarray (21, 3),
                    "normalized_landmarks": np.ndarray (21, 3)
                }
            """
            results = self.hands.process(rgb_image)

            if not results.multi_hand_landmarks:
                return [], []

            output = []

            for hand_landmarks, handedness_info in zip(
                results.multi_hand_landmarks,
                results.multi_handedness,
            ):
                handedness = handedness_info.classification[0].label

                raw_landmarks = self._landmarks_to_numpy(hand_landmarks)
                normalized_landmarks = self.normalize_hand_landmarks(raw_landmarks)

                output.append(
                    {
                        "handedness": handedness,
                        "raw_landmarks": raw_landmarks,
                        "normalized_landmarks": normalized_landmarks,
                    }
                )

            return results, output
        
        @staticmethod
        def _landmarks_to_numpy(hand_landmarks) -> np.ndarray:
            """
            Convert MediaPipe landmarks to numpy array (21, 3).
            Coordinates are in normalized image space.
            """
            return np.array(
                [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark],
                dtype=np.float32,
            )
        
        def flatten_hand_landmarks(self, row):
            """
            Converts left and right hand landmarks into a single flat feature vector.
            Missing hands are replaced with zeros.
            """
            left = row["left_hand_landmarks"]
            right = row["right_hand_landmarks"]
            
            # 21 landmarks x 3 coordinates = 63
            left_flat = np.array(left).flatten() if left is not None else np.zeros(63)
            right_flat = np.array(right).flatten() if right is not None else np.zeros(63)
            
            # Combine left + right -> 126 features
            return np.concatenate([left_flat, right_flat])
        
        def recv(self, frame):
            # self.frame_count += 1
            # if self.frame_count % 30 == 0:
            #     fps = self.frame_count / (time.time() - self.start_time)
            #     print(f"Video FPS: {fps:.2f}")
            
            if self.target_sign != self.previous_target_sign:
                print(f'Target sign changed to: {self.target_sign}')
                self.previous_target_sign = self.target_sign
                self.first_match_time = None
            
            try:
                img = frame.to_ndarray(format="bgr24")
                img_h, img_w, _ = img.shape
                img = cv2.flip(img, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                raw_results, hands = self.process_image(img_rgb)

                # Calculate dynamic font size scale and thickness
                # 640 is the reference width. If width drops to 320, scale drops to 0.5
                base_scale = 1.0
                font_scale = base_scale * (img_w / 640.0)
                
                left_hand = None
                right_hand = None
                for hand in hands:
                    if hand["handedness"] == "Left":
                        left_hand = hand["normalized_landmarks"].tolist()
                    elif hand["handedness"] == "Right":
                        right_hand = hand["normalized_landmarks"].tolist()

                landmarks = {"left_hand_landmarks": left_hand,
                            "right_hand_landmarks": right_hand,
                            }
                feature_vector = self.flatten_hand_landmarks(landmarks)
            
                # Skip prediction during cooldown
                if self.in_cooldown:
                    elapsed = time.time() - self.last_success_time
                    if elapsed >= self.success_cooldown:
                        self.in_cooldown = False
                    else:
                        # Add success maeesage
                        img = self.draw_modern_text(img, self.success_msg, y_pos=40, font_size=50, color=(0, 255, 0)) # Centered, Large, Green
                        if self.success_cooldown > 1:
                            # Calculate remaining seconds
                            time_left = math.ceil(self.success_cooldown - elapsed)
                            # Create countdown text
                            countdown_text = f"Try again in {time_left}..."
                            # Draw small orange text at the bottom
                            # Get image height to position text at the bottom
                            h, w = img.shape[:2]
                            img = self.draw_modern_text(img, countdown_text, y_pos=h - 40, font_size=25, color=(255, 180, 0))
                
                # LSTM SLIDING WINDOW LOGIC
                if self.category != 'ABC':
                    self.sequence_buffer.append(feature_vector)
                    # Keep only the last sequence_length frames
                    self.sequence_buffer = self.sequence_buffer[-self.sequence_length:]

                # Draw Landmarks
                if raw_results and raw_results.multi_hand_landmarks:
                    for hand_landmarks in raw_results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(img,
                                                       hand_landmarks,
                                                       self.mp_hands.HAND_CONNECTIONS,
                                                       self.landmark_style,
                                                       self.connection_style,
                                                       )
                            
                    # Prediction logic
                    if not self.in_cooldown and self.model and (self.category == 'ABC' or len(self.sequence_buffer) == self.sequence_length):
                        # print(f"Category: {self.category}")
                        if self.category == 'ABC':
                            probas = self.model.predict_proba(feature_vector.reshape(1, -1))[0]
                        else:
                            # print(f"Buffer Check: {self.sequence_buffer[-1][0]}")
                            input_tensor = torch.FloatTensor(np.array([self.sequence_buffer])).to('cpu') # or 'cuda'
                            # Get Prediction
                            with torch.no_grad():
                                # call the model (assumes model is the PyTorch class instance)
                                output = self.model(input_tensor) 
                                probas = torch.softmax(output, dim=1).numpy()[0]

                        conf = np.max(probas)
                        label = self.model_classes[np.argmax(probas)]
                        target_sign_idx = self.model_classes.index(self.target_sign)
                        target_prob = probas[target_sign_idx]
                        # Calculate Rank: How many classes have a lower probability than our target?
                        # (0 = worst, N-1 = best)
                        target_rank = np.sum(probas < target_prob)
                        max_rank = len(probas) - 1 if len(probas) > 1 else 1
                        # Normalize rank to 0.0 - 1.0
                        target_rank_norm = target_rank / max_rank

                        # set frame characteristics
                        # Interpolate Color from Red (0.0) to Green (1.0)
                        # BGR Format: Red is (0, 0, 255), Green is (0, 255, 0)
                        green_component = int(255 * target_rank_norm)
                        red_component = int(255 * (1 - target_rank_norm))
                        frame_color = (0, green_component, red_component)
                        frame_thickness = self.init_frame_thickness # Base width in pixels
                        
                        if label:
                            # Draw Prediction
                            # prediction_text = f"Pred: {label} ({conf:.2f})"
                            # cv2.putText(img, prediction_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                            # img = self.draw_text_with_pil(img, prediction_text, (10, 20), font_size=40, color=(0, 255, 0))
                            # img = self.draw_modern_text(img, prediction_text, y_pos=20, font_size=30, color=(200, 200, 200), centered=False)
                            
                            # Check Success
                            # Handle potential case mismatch or type mismatch
                            # print(f'self.target_sign: {self.target_sign}, label: {label}')
                            if self.target_sign and \
                                str(label).strip().lower() == str(self.target_sign).strip().lower() and \
                                (self.category=='ABC' or conf >= self.prediction_threshold):

                                holding_t_diff = time.time() - self.first_match_time if self.first_match_time else 0
                                # print(f't_diff: {t_diff}')
                                
                                if not self.reset_hand:
                                    # cv2.putText(img, "Reset Hand", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 125, 255), 3, cv2.LINE_AA)
                                    if not self.in_cooldown:
                                        img = self.draw_modern_text(img, self.reset_msg, y_pos=40, font_size=40, color=(255, 180, 0)) # light blue
                                    
                                elif self.first_match_time is None:
                                    self.first_match_time = time.time()
                                    self.in_cooldown = False

                                elif holding_t_diff >= self.hold_sign_duration:
                                    self.in_cooldown = True
                                    self.first_match_time = None
                                    self.reset_hand = False
                                    self.last_success_time = time.time()
                                    self.success_msg = random.choice(self.success_messages)
                                    # print("SUCCESS!!!!!!!!!!!!!!!!!!!!!!!!!")

                                    if self.result_queue:
                                        self.result_queue.put("success")

                                    # Immediate visual feedback on frame
                                    # cv2.putText(img, "SUCCESS!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3, cv2.LINE_AA)

                                else:
                                    # print("Holding correct sign...")
                                    frame_thickness += int(2 * float(holding_t_diff) * frame_thickness)
                                    # print(f'frame_thickness: {frame_thickness}')
                                    # Immediate visual feedback on frame
                                    # cv2.putText(img, "Hold...", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3, cv2.LINE_AA)
                                    img = self.draw_modern_text(img, self.hold_msg, y_pos=40, font_size=40, color=(30, 200, 0)) # Centered, Medium, green
                                    self.in_cooldown = False
                            else:
                                self.first_match_time = None
                                self.reset_hand = True
                            
                            # draw translucent feedback frame
                            alpha = 0.5 * np.min((1.8, frame_thickness/self.init_frame_thickness))
                            # print(f'alpha: {alpha}')
                            overlay = img.copy()
                            cv2.rectangle(overlay, (0, 0), (img_w, img_h), frame_color, int(frame_thickness * 2))
                            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
                
                else:
                    self.reset_hand = True
                                                
            except Exception as e:
                print(f"Frame processing error:\n{traceback.format_exc()}", flush=True)

            return av.VideoFrame.from_ndarray(img, format="bgr24")
        
else:
    print("NO WEBRTC")
    class HandLandmarkProcessor:
        pass
