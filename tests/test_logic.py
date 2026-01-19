import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.localization import get_string
from utils.state import init_state, get_progress, increment_progress
import streamlit as st

# Mock session state for testing
class MockSessionState(dict):
    def __getattr__(self, item):
        return self.get(item)
    def __setattr__(self, key, value):
        self[key] = value

if "session_state" not in st.__dict__:
    st.session_state = MockSessionState()

def test_localization():
    assert get_string("welcome", "en") == "Welcome to Sign Language Learning"
    assert get_string("welcome", "he") == "ברוכים הבאים ללימוד שפת סימנים"
    assert get_string("unknown_key", "en") == "unknown_key"
    print("Localization tests passed.")

def test_state_logic():
    init_state()
    assert st.session_state.page == "home"
    assert st.session_state.app_lang == "en"
    
    # Test progress
    st.session_state.user_progress = {}
    increment_progress("ASL", "ABC", "A")
    assert get_progress("ASL", "ABC", "A") == 1
    
    increment_progress("ASL", "ABC", "A")
    increment_progress("ASL", "ABC", "A")
    assert get_progress("ASL", "ABC", "A") == 3
    
    increment_progress("ASL", "ABC", "A")
    assert get_progress("ASL", "ABC", "A") == 3 # Should stay at 3
    
    print("State logic tests passed.")

if __name__ == "__main__":
    test_localization()
    test_state_logic()
