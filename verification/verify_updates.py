from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 1. Go to Home
        print("Navigating to Home...")
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")
        
        # Check Dark Mode (via Settings)
        # We can't easily check visual color, but we can check if settings page exists
        print("Opening Settings...")
        page.locator("button").first.click() # Assuming gear is first button or top right
        # Actually, in home view, gear is top right.
        
        # Navigate to Guest
        print("Going to Guest...")
        page.goto("http://localhost:8501")
        page.get_by_text("Guest", exact=True).click()
        time.sleep(1)
        
        # Select ASL
        print("Selecting ASL...")
        page.get_by_text("ASL (American Sign Language)").click()
        time.sleep(1)
        
        # Select Basics
        print("Selecting Basics...")
        page.get_by_text("Basics").click()
        time.sleep(3)
        
        print("Verifying Layout...")
        # Check for scrollable container (roughly)
        # We can look for the container div
        
        # Take screenshot of Learning Screen with new layout
        page.screenshot(path="verification/05_new_layout.png")
        
        # Check Feedback Popover
        print("Checking Feedback Menu...")
        # Find a button with "more_vert" or just the small column button.
        # Since we use st.popover("⋮"), we search for that text
        try:
            popover_btn = page.get_by_text("⋮").first
            popover_btn.click()
            time.sleep(1)
            page.screenshot(path="verification/06_feedback_open.png")
            print("Feedback menu opened.")
            
            # Click "Flag for later"
            print("Clicking Flag...")
            page.get_by_text("Flag for later").click()
            time.sleep(1)
            # Verify toast? Hard in screenshot, but script runs means no crash.
            
        except Exception as e:
            print(f"Feedback check failed: {e}")

        # Check Back Button
        print("Checking Back Button...")
        # Should be "<"
        try:
            back_btn = page.get_by_text("<", exact=True).first
            if back_btn:
                print("Back button found.")
                back_btn.click()
                time.sleep(1)
                # Should be back to Category selection
                page.screenshot(path="verification/07_back_nav.png")
        except Exception as e:
            print(f"Back button check failed: {e}")

        browser.close()

if __name__ == "__main__":
    run()
