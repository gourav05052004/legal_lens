import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def keep_alive():
    url = "https://legal-lens-ai.streamlit.app/"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"Opening {url}...")
        driver.get(url)
        
        try:
            # Wait up to 15 seconds for the button to appear
            button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Yes, get this app back up!')]"))
            )
            button.click()
            print("App woken up ✅")
            time.sleep(5) # Give it a moment to process the click
        except Exception:
            print("App already awake ✅")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    keep_alive()
