# How to connect Gemini API Key

To use the AI capabilities in SAMANVAYA, you need a Google Gemini API Key. Follow these steps:

## Step 1: Get an API Key
1. Go to **Google AI Studio** (https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click on the **Get API key** button.
4. Create a new API key and copy it to your clipboard.

## Step 2: Add it to the Application
1. In the `SAMANVAYA` project folder (where `app.py` is), create a new file named exactly `.env`.
2. Open the `.env` file and paste your key in the following format:
   ```
   GEMINI_API_KEY=your_copied_api_key_here
   ```
3. Save the file.

*(Note: Never share your `.env` file publicly. It is automatically ignored in most secure setups).*

## Step 3: Restart the Server
If the server is currently running, stop it (Ctrl+C) and run it again:
```bash
python app.py
```

The system will automatically load the key from the `.env` file and use real Gemini Prompt Transformations!
