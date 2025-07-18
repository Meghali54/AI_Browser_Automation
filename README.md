
# AI Browser Automation Agent

This project demonstrates an AI agent that controls a real web browser through natural language conversation. It uses Selenium for browser automation (not APIs) and a React frontend for chat and screenshot display.

---

## 🗺️ High-Level Architecture

```mermaid
flowchart TD
    User[User] -->|Chat| Frontend[React Chat UI]
    Frontend -->|REST API| Backend[Flask + Selenium Backend]
    Backend -->|Controls| Browser[Chrome/Edge (Selenium)]
    Browser -->|Screenshots| Backend
    Backend -->|Screenshots/Status| Frontend
    Frontend -->|Displays| User
```

---

## ❗ Explicit Note

**This project uses browser automation (Selenium) to interact with Gmail and the web UI. No APIs are used for sending emails or accessing Gmail. All actions are performed by controlling a real browser.**

---

## ⚙️ Browser Automation Logic

1. The backend receives user commands and uses NLU to extract intent and details (e.g., recipient, subject, body).
2. Selenium launches a real browser (Chrome/Edge) and navigates to Gmail.
3. The script logs in, clicks Compose, fills in the recipient, subject, and body fields, and clicks Send—mimicking a real user.
4. At each step, the backend captures a screenshot and sends it to the frontend for display.
5. The frontend shows the screenshots inline with the chat, so the user can see every browser action.

---

## 🛠️ Tech Stack & Rationale

- **Python + Flask**: Simple, fast backend for REST API and orchestration.
- **Selenium**: Industry-standard for browser automation; allows full control of browser UI (required for this assignment).
- **React (Vite)**: Modern, fast frontend for chat UI and dynamic screenshot display.
- **Chrome/Edge**: Widely supported browsers for Selenium automation.

---

## 🚀 How to Run Locally

### Backend
1. Open a terminal and activate the virtual environment:
   ```powershell
   .\selenium_backend\Scripts\activate
   ```
2. Run the Flask backend:
   ```powershell
   python app.py
   ```

### Frontend
1. Open a new terminal and navigate to the frontend directory:
   ```powershell
   cd frontend
   ```
2. Start the React app:
   ```powershell
   npm run dev
   ```

---

## 🖼️ Sample Screenshots

Below are sample screenshots from the browser automation flow (see the `screenshots/` folder for more):

| Gmail Login | Compose | Fields Filled | Sent Confirmation |
|-------------|---------|--------------|------------------|
| ![Login](selenium_backend/screenshots/sample_login.png) | ![Compose](selenium_backend/screenshots/sample_compose.png) | ![Filled](selenium_backend/screenshots/sample_filled.png) | ![Sent](selenium_backend/screenshots/sample_sent.png) |

You can also record a GIF of the flow using a tool like ScreenToGif for demo purposes.

---

## 🧩 Challenges & Solutions

- **Gmail popups/overlays blocking actions**: Added robust popup dismissal logic and retries before every critical action.
- **Chrome profile/sign-in popup**: Detected and closed Chrome's own overlays using custom selectors.
- **Element not interactable errors**: Added explicit waits, focus/click, and attribute checks before sending keys to fields.
- **Frontend-backend connectivity**: Used Vite proxy and CORS to ensure smooth API communication.
- **No API usage allowed**: All email actions are performed via browser UI, not Gmail APIs.

---

## Requirements

## Structure
- `selenium_backend/`: Python backend with Flask, Selenium, and REST API
- `frontend/`: React app (Vite) for chat UI and screenshot display

## How it works
1. User enters a natural language command in the React chat UI.
2. The frontend sends the command to the Flask backend.
3. The backend uses NLU to extract intent and details, then controls a real browser with Selenium (e.g., to send an email via Gmail).
4. After each browser action, the backend captures a screenshot and sends it to the frontend.
5. The frontend displays the screenshots inline with the conversation.

## Getting Started

### Backend
1. Open a terminal and activate the virtual environment:
   ```powershell
   .\selenium_backend\Scripts\activate
   ```
2. Run the Flask backend:
   ```powershell
   python app.py
   ```

### Frontend
1. Open a new terminal and navigate to the frontend directory:
   ```powershell
   cd frontend
   ```
2. Start the React app:
   ```powershell
   npm run dev
   ```

## Requirements
- Python 3.8+
- Node.js 18+
- Chrome or Edge browser installed (for Selenium)

## Notes
- No APIs are used for Gmail; all actions are performed via browser automation.
- Replace any placeholder credentials with your own for testing.
