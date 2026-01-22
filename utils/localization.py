
STRINGS = {
    "en": {
        "welcome": "Welcome to AI-SL",
        "subtitle": "Learning ASL & ISL with AI!",
        "login": "Login",
        "signup": "Sign Up",
        "guest": "Guest",
        "settings_title": "Settings",
        "about_title": "About",
        "language": "App Language",
        "sound": "Sound",
        "theme": "Theme (Light/Dark)",
        "back_home": "Back to Home",
        "select_learning_lang": "What would you like to learn?",
        "isl": "ISL (Israeli Sign Language)",
        "asl": "ASL (American Sign Language)",
        "signs_learned": "signs learned",
        "select_category": "Select Category",
        "cat_abc": "ABC",
        "cat_basics": "Basics",
        "cat_questions": "Questions",
        "cat_animals": "Animals",
        "cat_fingerspelling": "Custom Fingerspelling Practice",
        "category_mastered": "Completed",
        "learning_title": "Learning",
        "fingerspelling_title": "Fingerspelling Practice",
        "enter_word": "Enter a word to practice",
        "start_practice": "Start Practice",
        "prev_letter": "Previous Letter",
        "next_letter": "Skip Letter",
        "show_instructions": "Show Instructions",
        "hide_instructions": "Hide Instructions",
        "video_device": "Select Video Device",
        "progress": "Progress",
        "success_msg": "Good job!",
        "instructions_placeholder": "Instructions for sign: {}",
        "simulate_success": "Simulate Success",
        "about_content": """
        ### About the System
        
        This application uses advanced computer vision techniques to help you learn Sign Language (ASL and ISL) by providing live feedback on your signing.
        
        **How it works:**
        1. Select a sign to learn.
        2. Watch the instructions.
        3. Perform the sign in front of your camera.
        4. The system analyzes your hand movements and provides feedback.
        
        **Limitations:**
        Please note that this is an AI-based system and mistakes are possible. 
        - **False Detections:** The system might incorrectly approve a wrong sign.
        - **Failures to Detect:** The system might fail to recognize a correct sign due to lighting, angle, or background clutter.
        
        **Privacy:**
        Everything runs locally in your browser/app session. No video data is sent to external servers for processing.
        
        We appreciate your feedback to help us improve!
        """,
        "disclaimer": "False detections and failures to detect signs may occur, please leave feedback if so.",
        "feedback_fail_detect": "Failed to detect signing",
        "feedback_incorrect": "Detected incorrect sign",
        "feedback_flag": "Save for later",
        "feedback_thank_you": "Thank you for your feedback!",
        "flag_saved": "Saved for later!"
    },
    "he": {
        "welcome": "ברוכים הבאים ל-AI-SL",
        "subtitle": "לומדים ASL ו-ISL עם בינה מלאכותית!",
        "login": "התחברות",
        "signup": "הרשמה",
        "guest": "אורח",
        "settings_title": "הגדרות",
        "about_title": "אודות",
        "language": "שפת האפליקציה",
        "sound": "צליל",
        "theme": "ערכת נושא (בהיר/כהה)",
        "back_home": "חזרה לדף הבית",
        "select_learning_lang": "מה נלמד היום?",
        "isl": "שפת סימנים ישראלית (ISL)",
        "asl": "שפת סימנים אמריקאית (ASL)",
        "signs_learned": "סימנים נלמדו",
        "select_category": "בחר קטגוריה",
        "cat_abc": "אלף-בית",
        "cat_basics": "בסיס",
        "cat_questions": "שאלות",
        "cat_animals": "חיות",
        "cat_fingerspelling": "אימון איות מותאם אישית",
        "category_mastered": "הושלם",
        "learning_title": "לומדים",
        "fingerspelling_title": "אימון איות",
        "enter_word": "הכנס מילה לאימון",
        "start_practice": "התחל אימון",
        "prev_letter": "אות קודמת",
        "next_letter": "דלג על אות",
        "show_instructions": "הצג הוראות",
        "hide_instructions": "הסתר הוראות",
        "video_device": "בחר התקן וידאו",
        "progress": "התקדמות",
        "success_msg": "כל הכבוד!",
        "instructions_placeholder": "הוראות לסימן: {}",
        "simulate_success": "הדמה הצלחה",
        "about_content": """
        ### אודות המערכת
        
        אפליקציה זו משתמשת בטכנולוגיות ראייה ממוחשבת מתקדמות כדי לעזור לך ללמוד שפת סימנים (ASL ו-ISL) על ידי מתן משוב חי.
        
        **איך זה עובד:**
        1. בחר סימן ללימוד.
        2. צפה בהוראות.
        3. בצע את הסימן מול המצלמה.
        4. המערכת מנתחת את תנועות הידיים ומספקת משוב.
        
        **מגבלות:**
        שים לב כי זוהי מערכת מבוססת בינה מלאכותית וייתכנו טעויות.
        - **זיהויים שגויים:** המערכת עשויה לאשר בטעות סימן שגוי.
        - **אי-זיהוי:** המערכת עשויה שלא לזהות סימן נכון בגלל תאורה, זווית או רקע עמוס.
        
        **פרטיות:**
        הכל רץ באופן מקומי בדפדפן/אפליקציה שלך. שום מידע וידאו לא נשלח לשרתים חיצוניים לעיבוד.
        
        אנו מעריכים את המשוב שלך כדי לעזור לנו להשתפר!
        """,
        "disclaimer": "ייתכנו זיהויים שגויים ואי-זיהוי של סימנים, אנא השאר משוב אם נתקלת בכך.",
        "feedback_fail_detect": "נכשל בזיהוי הסימון",
        "feedback_incorrect": "זוהה סימן שגוי",
        "feedback_flag": "לשמור לאחר כך",
        "feedback_thank_you": "תודה על המשוב!",
        "flag_saved": "נשמר לאחר כך!"
    }
}

def get_string(key, lang="en"):
    return STRINGS.get(lang, STRINGS["en"]).get(key, key)
