1. Get the google Gemini API Key: https://www.youtube.com/watch?v=6BRyynZkvf0

2. Update .env with your Gemini API Key.

GOOGLE_AI_API_KEY=your-key-here

Don't worry about GOOGLE_SEARCH_API_KEY or SEARCH_ENGINE_ID,
I was experimenting with Google Search to find the form URL, but no luck.

3. Install UV. UV is a project manager for Python. It will install python and its packages automatically.

3.1 Open Powershell in Windows. Paste this command:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"


3.2 Otherwise, follow official instruction for Mac/Linux.
https://docs.astral.sh/uv/getting-started/installation/ 

4. Open config.py, set HEADLESS to False if you want to selenium window opened, vice versa.

5. We are ready. In Windows, we can double click start.bat to start the app.

5.1 In Linux or MacOs, you have to run start.sh to start the app and stop.sh to stop.