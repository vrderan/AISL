from playwright.sync_api import sync_playwright
import time

def verify_changes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. Home
        page.goto("http://localhost:8501")
        time.sleep(3)
        
        # 2. Go to ISL ABC Learning
        page.get_by_role("button", name="Guest").click()
        time.sleep(2)
        page.get_by_role("button", name="ISL").click()
        time.sleep(2)
        page.get_by_role("button", name="ABC").click()
        time.sleep(2)
        
        # 3. Check for Hebrew Letters (Aleph)
        # We need to verify if the button text contains Hebrew
        page.screenshot(path="verification/05_isl_abc.png")
        print("ISL ABC screenshot taken. Check for Hebrew letters.")
        
        # 4. Select a sign -> Check Blue Styling
        # Click the first sign (Aleph)
        page.locator("button").filter(has_text="0/3").first.click()
        time.sleep(2)
        page.screenshot(path="verification/06_isl_selected.png")
        print("Selected sign screenshot taken. Check for Blue/Highlight.")

        # 5. Simulate Success 3 times -> Check Green Styling
        # "Simulate Success" button
        for _ in range(3):
            page.get_by_text("Simulate Success").click()
            time.sleep(1)
        
        page.screenshot(path="verification/07_isl_mastered.png")
        print("Mastered sign screenshot taken. Check for Green.")

        browser.close()

if __name__ == "__main__":
    verify_changes()
