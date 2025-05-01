from flask import Flask, render_template, request, jsonify
import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import bot handlers
from bot import start, help_command, handle_video, handle_document, handle_text, handle_unknown

app = Flask(__name__)

# Initialize bot application
bot_app = Application.builder().token(TELEGRAM_TOKEN).build()

@app.route('/')
def index():
    # Set the correct bot username for the link
    bot_username = "gggyyyyyyyyyyyytBOT"  # This is the confirmed username from our API check
    bot_link = f"https://t.me/{bot_username}"
    
    return f"""
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video Screenshot Bot</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
            body {{
                padding: 2rem;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            .hero {{
                padding: 4rem 0;
                text-align: center;
                background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1626379953822-baec19c3accd?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80');
                background-size: cover;
                background-position: center;
                color: white;
                border-radius: 1rem;
                margin-bottom: 3rem;
            }}
            .features {{
                margin: 3rem 0;
            }}
            .feature-card {{
                height: 100%;
                transition: transform 0.3s ease;
                border: none;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .feature-card:hover {{
                transform: translateY(-5px);
            }}
            .feature-icon {{
                font-size: 2.5rem;
                margin-bottom: 1rem;
                color: var(--bs-primary);
            }}
            .how-to-use {{
                background-color: rgba(13, 110, 253, 0.1);
                padding: 3rem;
                border-radius: 1rem;
            }}
            .step {{
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
            }}
            .step-number {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-color: var(--bs-primary);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-right: 1rem;
            }}
            footer {{
                margin-top: auto;
                padding-top: 3rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1 class="display-4">Video Screenshot Bot</h1>
                <p class="lead fs-4 mb-4">Extract screenshots from videos at 1-second intervals</p>
                <a href="{bot_link}" class="btn btn-primary btn-lg px-5" target="_blank">
                    <i class="bi bi-telegram me-2"></i> Open Bot on Telegram
                </a>
            </div>
            
            <div class="features">
                <div class="row row-cols-1 row-cols-md-3 g-4">
                    <div class="col">
                        <div class="card feature-card">
                            <div class="card-body text-center p-4">
                                <div class="feature-icon">
                                    <i class="bi bi-camera"></i>
                                </div>
                                <h4 class="card-title">Extract Frames</h4>
                                <p class="card-text">Automatically takes screenshots at 1-second intervals from your videos up to 30 seconds long.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col">
                        <div class="card feature-card">
                            <div class="card-body text-center p-4">
                                <div class="feature-icon">
                                    <i class="bi bi-lightning-charge"></i>
                                </div>
                                <h4 class="card-title">Quick Processing</h4>
                                <p class="card-text">Fast and efficient processing that delivers your screenshots in seconds.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col">
                        <div class="card feature-card">
                            <div class="card-body text-center p-4">
                                <div class="feature-icon">
                                    <i class="bi bi-hand-thumbs-up"></i>
                                </div>
                                <h4 class="card-title">Easy to Use</h4>
                                <p class="card-text">Just send your video to the bot on Telegram and get your screenshots instantly.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="how-to-use text-center mt-5">
                <h2 class="mb-4">How to Use</h2>
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="step">
                            <div class="step-number">1</div>
                            <div class="text-start">Find the bot on Telegram by clicking the link or searching for its username</div>
                        </div>
                        <div class="step">
                            <div class="step-number">2</div>
                            <div class="text-start">Send a video (up to 30 seconds long) to the bot</div>
                        </div>
                        <div class="step">
                            <div class="step-number">3</div>
                            <div class="text-start">Receive screenshots taken at 1-second intervals</div>
                        </div>
                        <div class="mt-4">
                            <a href="{bot_link}" class="btn btn-primary btn-lg" target="_blank">
                                <i class="bi bi-telegram me-2"></i> Start Using Now
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <footer class="text-center text-muted">
                <p>Video Screenshot Bot is currently running and ready to process your videos!</p>
                <p class="mb-0">© 2025 Video Screenshot Bot</p>
            </footer>
        </div>
    </body>
    </html>
    """

# Health check endpoint for uptime monitoring
@app.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint to keep the service awake"""
    return jsonify({"status": "ok", "message": "Bot is running"}), 200

# Webhook endpoint for Telegram
@app.route('/webhook', methods=['POST'])
async def webhook():
    """Webhook endpoint for Telegram to send updates"""
    if request.method == 'POST':
        try:
            # Parse update from Telegram
            update_dict = json.loads(request.get_data().decode('utf-8'))
            update = Update.de_json(update_dict, bot_app.bot)
            
            # Process the update
            await bot_app.process_update(update)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            logger.error(f"Error processing webhook update: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "ok"}), 200

# Setup webhook function
def setup_webhook(webhook_url):
    """Setup webhook for Telegram bot"""
    # Register command handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    
    # Register message handlers
    bot_app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    bot_app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    bot_app.add_handler(MessageHandler(filters.COMMAND, handle_unknown))
    
    # Set up webhook
    bot_app.bot.set_webhook(url=f"{webhook_url}/webhook")
    logger.info(f"Webhook set to {webhook_url}/webhook")

if __name__ == '__main__':
    # If running locally, get webhook URL from environment variable or use default
    webhook_url = os.environ.get('WEBHOOK_URL', 'https://your-render-app-name.onrender.com')
    
    # Setup the webhook
    setup_webhook(webhook_url)
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)