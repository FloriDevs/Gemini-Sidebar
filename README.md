# Gemini-Sidebar

A sidebar that lets you chat with Gemini (via the API) and allows it to run commands for you on your computer.

## 🚀 Features

- **Chat with Gemini:** Converse directly with the AI in a convenient sidebar.
- **PC Control:** Let Gemini execute actions and commands on your computer.

---

## 🛠️ Installation & Setup (First-Time Setup)

Follow these steps to set up the project for the first time:

1. **Create a virtual environment (venv):**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install google-genai pillow pyautogui
   ```

4. **Get an API key:**
   Get your free API key from [Google AI Studio](https://aistudio.google.com/api-keys).

5. **Set the API key as an environment variable:**
   ```bash
   export GEMINI_API_KEY="[your_api_key_here]"
   ```

6. **Run the application:**
   ```bash
   python3 sidebar.py
   ```

---

## 🔄 Running the App Again

To run the program again later, use these steps:

1. **Activate the virtual environment** (if not already active):
   ```bash
   source venv/bin/activate
   ```

2. **Set the API key again:**
   ```bash
   export GEMINI_API_KEY="[your_api_key_here]"
   ```

3. **Launch the app:**
   ```bash
   python3 sidebar.py
   ```
