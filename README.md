# Voice of the Streets
An NLP-based chatbot for citizen engagement in Sri Lanka.

## Features
- Report issues (e.g., "Power outage in Colombo").
- Upvote urgent concerns (50+ votes = "Push Now").
- Suggest donation links.
- Receive updates.

## Setup in GitHub Codespaces
1. Open this repo in Codespaces.
2. Activate venv: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up `.env` with Supabase and Telegram credentials (see `.env.example`).
5. Run web app: `python3 app.py` (access via Codespaces Ports tab, port 8000).
6. Run Telegram bot: `python3 interfaces/telegram_bot.py` (test in Telegram).

## Deployment
- **Web App**: Deployed for free on Render: [Live URL](https://voice-of-the-streets.onrender.com).
- **Telegram Bot**: Runs locally in Codespaces (see Future Work for full deployment).

## Demo
- **Web Interface**: Test locally or on Render.
  ![Web Screenshot](web_screenshot.png)
- **Telegram Interface**: Test in Codespaces.
  ![Telegram Screenshot](telegram_screenshot.png)

## Future Work
- Deploy Telegram bot using a free webhook service (e.g., ngrok + Render).
- Enhance NLP with fine-tuned models.

## License
MIT