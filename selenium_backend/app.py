

from flask import Flask, request, jsonify, send_file, session
try:
    from flask_cors import CORS
except ImportError:
    raise ImportError("flask_cors is not installed. Please install it with 'pip install flask-cors'.")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re

app = Flask(__name__)
app.secret_key = 'dev'  # For demo only, not secure
CORS(app, supports_credentials=True)

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), 'screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# In-memory session state for demo (not for production)
user_state = {}

app = Flask(__name__)
CORS(app)

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), 'screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Comment out headless for debugging
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    user_id = data.get('user_id', 'default')
    command = data.get('command', '').strip()
    state = user_state.get(user_id, {})

    # Step 1: Detect intent
    if not state.get('intent'):
        if re.search(r'leave application', command, re.I):
            state['intent'] = 'send_leave_email'
            user_state[user_id] = state
            return jsonify({'status': "I'll help you send that leave application. To access your email, I'll need your Gmail credentials. What's your email address?", 'expect': 'email'})
        else:
            return jsonify({'status': "Sorry, I can only help with sending leave application emails for now."})

    # Step 2: Collect email
    if not state.get('email'):
        if re.match(r'.+@.+\..+', command):
            state['email'] = command
            user_state[user_id] = state
            return jsonify({'status': "Thanks! And what's the password for this account? (Please use only a test account for this assignment)", 'expect': 'password'})
        else:
            return jsonify({'status': "What's your email address?", 'expect': 'email'})

    # Step 3: Collect password
    if not state.get('password'):
        if len(command) > 3:
            state['password'] = command
            user_state[user_id] = state
            return jsonify({'status': "Great! Now, when will you be taking leave?", 'expect': 'leave_dates'})
        else:
            return jsonify({'status': "Please enter your password.", 'expect': 'password'})

    # Step 4: Collect leave dates
    if not state.get('leave_dates'):
        if len(command) > 3:
            state['leave_dates'] = command
            user_state[user_id] = state
            return jsonify({'status': "And what's your manager's email address?", 'expect': 'manager_email'})
        else:
            return jsonify({'status': "When will you be taking leave?", 'expect': 'leave_dates'})

    # Step 5: Collect manager email
    if not state.get('manager_email'):
        if re.match(r'.+@.+\..+', command):
            state['manager_email'] = command
            user_state[user_id] = state
        else:
            return jsonify({'status': "What's your manager's email address?", 'expect': 'manager_email'})

    # Step 6: Compose and send email
    # Compose subject and body
    subject = "Leave Application"
    body = f"Dear Manager,\n\nI would like to apply for leave from {state['leave_dates']}.\n\nThank you.\n\nRegards,"

    # --- Selenium automation with step-by-step status and screenshots ---
    driver = get_driver()
    screenshots = []
    steps = []
    try:
        steps.append("Opening Gmail website...")
        driver.get('https://mail.google.com/')
        time.sleep(5)
        screenshot_path = os.path.join(SCREENSHOT_DIR, f'{user_id}_step1_gmail_login.png')
        driver.save_screenshot(screenshot_path)
        screenshots.append(f'{user_id}_step1_gmail_login.png')

        steps.append("Clicking on Sign In...")
        # Gmail usually redirects to sign in, so just proceed
        screenshot_path = os.path.join(SCREENSHOT_DIR, f'{user_id}_step2_signin.png')
        driver.save_screenshot(screenshot_path)
        screenshots.append(f'{user_id}_step2_signin.png')

        steps.append("Entering your email address...")
        email_input = driver.find_element(By.XPATH, '//input[@type="email"]')
        email_input.send_keys(state['email'])
        email_input.send_keys(Keys.ENTER)
        time.sleep(3)
        screenshot_path = os.path.join(SCREENSHOT_DIR, f'{user_id}_step3_email_filled.png')
        driver.save_screenshot(screenshot_path)
        screenshots.append(f'{user_id}_step3_email_filled.png')

        steps.append("Entering password and signing in...")
        # Wait for password input to appear
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))
        )
        password_input.send_keys(state['password'])
        password_input.send_keys(Keys.ENTER)
        time.sleep(5)
        screenshot_path = os.path.join(SCREENSHOT_DIR, f'{user_id}_step4_password_filled.png')
        driver.save_screenshot(screenshot_path)
        screenshots.append(f'{user_id}_step4_password_filled.png')

        steps.append("Successfully logged in! Now clicking on Compose...")
        # Dismiss Gmail popups/overlays that may cover Compose
        popup_xpaths = [
            '//button[@name="ok"]',  # Notification
            '//button[@aria-label="Close"]',  # Generic close
            '//div[@role="dialog"]//button',  # Dialog close
            '//span[text()="Got it"]',  # "Got it" button
            '//button[@aria-label="Dismiss"]',
            '//span[text()="Dismiss"]',  # Dismiss tip in compose
        ]
        for xpath in popup_xpaths:
            try:
                popup_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                popup_btn.click()
                time.sleep(1)
            except Exception:
                pass

        # Try to find all Compose buttons and click the first visible one
        from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException
        time.sleep(2)  # Let UI settle
        for _ in range(3):
            try:
                compose_buttons = driver.find_elements(By.XPATH, '//div[text()="Compose"]')
                for btn in compose_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.5)
                        btn.click()
                        raise StopIteration
                time.sleep(2)
            except (ElementNotInteractableException, StaleElementReferenceException):
                time.sleep(2)
            except StopIteration:
                break
        else:
            raise Exception("Compose button not interactable after several attempts")
        time.sleep(2)
        screenshot_path = os.path.join(SCREENSHOT_DIR, f'{user_id}_step5_compose.png')
        driver.save_screenshot(screenshot_path)
        screenshots.append(f'{user_id}_step5_compose.png')


        # Wait for Compose popup to be fully ready
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'to'))
        )
        time.sleep(1)

        # Screenshot after Compose for debugging
        compose_debug_path = os.path.join(SCREENSHOT_DIR, f'{user_id}_step_compose_opened.png')
        driver.save_screenshot(compose_debug_path)
        screenshots.append(f'{user_id}_step_compose_opened.png')


        # Robustly fill recipient field (focus/click before send_keys, no clear())
        for _ in range(3):
            to_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, 'to')))
            if to_input.is_displayed() and to_input.is_enabled():
                try:
                    to_input.click()
                except Exception:
                    pass
                time.sleep(0.5)
                if not to_input.get_attribute('readonly'):
                    to_input.send_keys(state['manager_email'])
                    break
            time.sleep(1)
        else:
            raise Exception("Recipient field not interactable after several attempts")

        # Robustly fill subject field (focus/click before send_keys, no clear())
        for _ in range(3):
            subject_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, 'subjectbox')))
            if subject_input.is_displayed() and subject_input.is_enabled():
                try:
                    subject_input.click()
                except Exception:
                    pass
                time.sleep(0.5)
                if not subject_input.get_attribute('readonly'):
                    subject_input.send_keys(subject)
                    break
            time.sleep(1)
        else:
            raise Exception("Subject field not interactable after several attempts")

        screenshot_path = os.path.join(SCREENSHOT_DIR, f'{user_id}_step6_filled_email.png')
        driver.save_screenshot(screenshot_path)
        screenshots.append(f'{user_id}_step6_filled_email.png')



        steps.append("Adding the email content I've generated...")
        body_filled = False
        for _ in range(5):
            body_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Message Body"]')))
            if body_input.is_displayed() and body_input.is_enabled():
                try:
                    body_input.click()
                    time.sleep(0.5)
                    # Try to focus with JS if needed
                    driver.execute_script("arguments[0].focus();", body_input)
                except Exception:
                    pass
                # Check for readonly and try send_keys
                if not body_input.get_attribute('readonly'):
                    try:
                        body_input.send_keys(body)
                        body_filled = True
                        break
                    except Exception as e:
                        steps.append(f'Error sending keys to body: {str(e)}')
            time.sleep(1)
        if not body_filled:
            # Screenshot for debugging
            error_body_path = os.path.join(SCREENSHOT_DIR, f'{user_id}_body_not_interactable.png')
            driver.save_screenshot(error_body_path)
            screenshots.append(f'{user_id}_body_not_interactable.png')
            raise Exception("Body field not interactable after several attempts (see screenshot)")

        screenshot_path = os.path.join(SCREENSHOT_DIR, f'{user_id}_step7_body.png')
        driver.save_screenshot(screenshot_path)
        screenshots.append(f'{user_id}_step7_body.png')

        steps.append("Clicking Send...")
        send_btn = driver.find_element(By.XPATH, '//div[text()="Send"]')
        send_btn.click()
        time.sleep(2)
        screenshot_path = os.path.join(SCREENSHOT_DIR, f'{user_id}_step8_sent.png')
        driver.save_screenshot(screenshot_path)
        screenshots.append(f'{user_id}_step8_sent.png')

        steps.append(f"✓ Email sent successfully! Your leave application has been sent to {state['manager_email']}.")
        status = 'success'
    except Exception as e:
        steps.append(f'Error: {str(e)}')
        status = 'error'
    finally:
        driver.quit()
        # Clear state for this user
        user_state.pop(user_id, None)

    # Return step-by-step messages and screenshots
    return jsonify({
        'status': status,
        'steps': steps,
        'screenshots': [f'/api/screenshot/{fname}' for fname in screenshots]
    })

@app.route('/api/screenshot/<filename>')
def get_screenshot(filename):
    path = os.path.join(SCREENSHOT_DIR, filename)
    if os.path.exists(path):
        return send_file(path, mimetype='image/png')
    return 'Not found', 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
