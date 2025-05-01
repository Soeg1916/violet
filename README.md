# Video Screenshot Telegram Bot

A Telegram bot that extracts screenshots from videos at 1-second intervals (up to 30 seconds of video) and sends them back to the user.

## Features

- Extract frames at 1-second intervals
- Support for videos up to 30 seconds long
- Support for various video formats (MP4, AVI, MOV)
- Clean and informative web interface
- Webhook mode for Render hosting

## Deployment on Render

### Prerequisites

1. A Telegram bot token from [@BotFather](https://t.me/BotFather)
2. A Render account (free tier is sufficient)

### Setup Steps

1. Fork this repository to your GitHub account
2. Log in to your Render account
3. Create a new Web Service
4. Connect your GitHub repository
5. Use the following settings:
   - **Name**: `video-screenshot-bot` (or any name you prefer)
   - **Environment**: Python
   - **Build Command**: `pip install flask flask-sqlalchemy gunicorn opencv-python python-telegram-bot python-dotenv psycopg2-binary`
   - **Start Command**: `gunicorn main:app`
   - **Plan**: Free

6. Add the following environment variables:
   - `TELEGRAM_TOKEN`: Your Telegram bot token
   - `WEBHOOK_URL`: The URL of your Render app (e.g., https://your-app-name.onrender.com)

7. Deploy the application

### Keeping the Bot Alive

Since Render's free tier puts services to sleep after 15 minutes of inactivity, you can:

1. Use a service like [UptimeRobot](https://uptimerobot.com/) to ping your `/ping` endpoint every 5 minutes
2. Set up a scheduled task in Render to ping your service periodically

## Local Development

1. Clone this repository
2. Set up a Python virtual environment
3. Install dependencies: `pip install flask flask-sqlalchemy gunicorn opencv-python python-telegram-bot python-dotenv psycopg2-binary`
4. Create a `.env` file with your `TELEGRAM_TOKEN`
5. Run the Flask app: `python main.py`

## Usage

1. Find the bot on Telegram (@gggyyyyyyyyyyyytBOT)
2. Send a video (up to 30 seconds long)
3. Receive screenshots taken at 1-second intervals