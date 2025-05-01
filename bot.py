#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Video Screenshot Telegram Bot - Rewritten for better reliability
This bot extracts screenshots from videos at 1-second intervals
(up to 30 seconds of video) and sends them back to the user.
"""

import os
import sys
import logging
import tempfile
from telegram import Update, InputMediaPhoto, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode
from utils import extract_frames, create_temp_dir, cleanup_temp_files
from config import TELEGRAM_TOKEN

# Improved logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# More focused logging for key components
logging.getLogger("telegram").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)

# Verify token is available and properly formatted
if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "":
    logger.error("TELEGRAM_TOKEN environment variable is not set")
    sys.exit(1)

logger.info(f"Bot token verification: {'*' * (len(TELEGRAM_TOKEN) - 8)}{TELEGRAM_TOKEN[-4:]}")

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Welcome to the Video Screenshot Bot!\n\n"
        "Send me a video (up to 30 seconds long) and I'll extract screenshots at 1-second intervals.\n\n"
        "Supported formats: MP4, AVI, MOV\n"
        "Maximum video length: 30 seconds\n\n"
        "Type /help for more information."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "📹 *Video Screenshot Bot Help*\n\n"
        "Just send me a video and I'll extract screenshots at 1-second intervals.\n\n"
        "*Supported video formats:*\n"
        "• MP4\n"
        "• AVI\n"
        "• MOV\n\n"
        "*Limitations:*\n"
        "• Maximum video length: 30 seconds\n"
        "• Maximum file size: 20MB (Telegram limitation)\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message",
        parse_mode="Markdown"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the video and send back screenshots."""
    
    # Log the received video
    logger.info(f"Received video message: {update.message.video.file_id}")
    logger.info(f"Video duration: {update.message.video.duration} seconds")
    
    # Send initial processing message
    processing_message = await update.message.reply_text(
        "🔄 Processing your video... This may take a moment."
    )
    
    try:
        # Create a temporary directory for storing frames
        temp_dir = create_temp_dir()
        
        # Get the video file
        video = await context.bot.get_file(update.message.video.file_id)
        
        # Check video duration
        duration = update.message.video.duration
        if duration > 30:
            await update.message.reply_text(
                "⚠️ Video is too long! The maximum supported duration is 30 seconds."
            )
            return
        
        # Download the video to a temporary file
        video_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        await video.download_to_drive(video_file.name)
        
        # Update user on progress
        await processing_message.edit_text("⏳ Downloading video complete. Extracting frames...")
        
        # Extract frames from the video
        frame_paths = extract_frames(video_file.name, temp_dir, interval=1)
        
        if not frame_paths:
            await update.message.reply_text(
                "⚠️ Could not extract any frames from the video. Please try a different video."
            )
            cleanup_temp_files([video_file.name], temp_dir)
            return
        
        # Update user on progress
        await processing_message.edit_text(
            f"✅ Extracted {len(frame_paths)} screenshots! Sending them now..."
        )
        
        # Send the frames back to the user
        from telegram import InputMediaPhoto
        
        # Log the frames we're about to send
        logger.info(f"Preparing to send {len(frame_paths)} frames as media group")
        
        # Process in batches of 10 (Telegram limitation)
        for i in range(0, len(frame_paths), 10):
            batch = frame_paths[i:i+10]
            logger.info(f"Sending batch {i//10 + 1} with {len(batch)} frames")
            
            # Create media group for this batch
            media_group = []
            for j, frame_path in enumerate(batch):
                # Create proper InputMediaPhoto object
                with open(frame_path, 'rb') as photo:
                    caption = f"Frame at {i+j+1}s" if j == 0 else ''
                    media_group.append(InputMediaPhoto(media=photo, caption=caption))
            
            # Send this batch
            try:
                await update.message.reply_media_group(media=media_group)
                logger.info(f"Successfully sent batch {i//10 + 1}")
            except Exception as e:
                logger.error(f"Error sending media group: {str(e)}")
                await update.message.reply_text(
                    f"Error sending screenshots batch {i//10 + 1}: {str(e)}"
                )
        
        await update.message.reply_text(
            f"✅ Successfully extracted and sent {len(frame_paths)} screenshots!"
        )
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        await update.message.reply_text(
            f"❌ An error occurred while processing your video: {str(e)}\n"
            "Please try again with a different video."
        )
    finally:
        # Clean up temporary files
        try:
            cleanup_temp_files([video_file.name], temp_dir)
        except:
            pass
        
        # Delete the processing message
        await processing_message.delete()

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document/file messages that may be videos."""
    # Log the received document
    logger.info(f"Received document: {update.message.document.file_name}")
    logger.info(f"Document mime type: {update.message.document.mime_type}")
    
    # Check if the document MIME type is a video
    mime_type = update.message.document.mime_type
    if mime_type and mime_type.startswith('video/'):
        processing_message = await update.message.reply_text(
            "🔄 Processing your video... This may take a moment."
        )
        
        try:
            # Create a temporary directory for storing frames
            temp_dir = create_temp_dir()
            
            # Get the video file
            video = await context.bot.get_file(update.message.document.file_id)
            
            # Download the video to a temporary file
            video_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            await video.download_to_drive(video_file.name)
            
            # Update user on progress
            await processing_message.edit_text("⏳ Downloading video complete. Extracting frames...")
            
            # Extract frames from the video
            frame_paths = extract_frames(video_file.name, temp_dir, interval=1, max_duration=30)
            
            if not frame_paths:
                await update.message.reply_text(
                    "⚠️ Could not extract any frames from the video or the video is longer than 30 seconds. "
                    "Please try a different video."
                )
                cleanup_temp_files([video_file.name], temp_dir)
                return
            
            # Update user on progress
            await processing_message.edit_text(
                f"✅ Extracted {len(frame_paths)} screenshots! Sending them now..."
            )
            
            # Send the frames back to the user - importing here to avoid potential import issues
            from telegram import InputMediaPhoto
            
            # Log the frames we're about to send
            logger.info(f"Preparing to send {len(frame_paths)} frames as media group")
            
            # Process in batches of 10 (Telegram limitation)
            for i in range(0, len(frame_paths), 10):
                batch = frame_paths[i:i+10]
                logger.info(f"Sending batch {i//10 + 1} with {len(batch)} frames")
                
                # Create media group for this batch
                media_group = []
                for j, frame_path in enumerate(batch):
                    # Create proper InputMediaPhoto object
                    with open(frame_path, 'rb') as photo:
                        caption = f"Frame at {i+j+1}s" if j == 0 else ''
                        media_group.append(InputMediaPhoto(media=photo, caption=caption))
                
                # Send this batch
                try:
                    await update.message.reply_media_group(media=media_group)
                    logger.info(f"Successfully sent batch {i//10 + 1}")
                except Exception as e:
                    logger.error(f"Error sending media group: {str(e)}")
                    await update.message.reply_text(
                        f"Error sending screenshots batch {i//10 + 1}: {str(e)}"
                    )
            
            await update.message.reply_text(
                f"✅ Successfully extracted and sent {len(frame_paths)} screenshots!"
            )
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            await update.message.reply_text(
                f"❌ An error occurred while processing your video: {str(e)}\n"
                "Please try again with a different video."
            )
        finally:
            # Clean up temporary files
            try:
                cleanup_temp_files([video_file.name], temp_dir)
            except:
                pass
            
            # Delete the processing message
            await processing_message.delete()
    else:
        # Not a video document
        await update.message.reply_text(
            "⚠️ Please send a video file. I only process videos in MP4, AVI, or MOV format."
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    await update.message.reply_text(
        "Please send me a video to extract screenshots. "
        "Type /help for more information."
    )

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    if update.message and update.message.text and update.message.text.startswith('/'):
        await update.message.reply_text(
            f"Sorry, I don't understand the command '{update.message.text}'.\n"
            "Type /help to see available commands."
        )

async def error_handler(update, context):
    """Log the error and send a message to the user if possible."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Try to notify user if possible
    try:
        if update and hasattr(update, 'effective_message') and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Sorry, something went wrong while processing your request.\n"
                "Please try again later or send a different video."
            )
    except Exception as e:
        logger.error(f"Failed to send error message to user: {e}")

def main() -> None:
    """Start the bot."""
    try:
        # First, test a simple connection to the API
        logger.info("Testing connection to Telegram API...")
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Create the Application
        logger.info("Creating application...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Add handlers in the right order (specific to general)
        logger.info("Registering handlers...")
        
        # Command handlers first (highest priority)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        
        # Specific content type handlers
        application.add_handler(MessageHandler(filters.VIDEO, handle_video))
        
        # Document handler for videos sent as files
        application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
        
        # Text message handler (except commands)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        # Unknown command handler
        application.add_handler(MessageHandler(filters.COMMAND, handle_unknown))
        
        # Debug handler (logs all messages)
        async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            """Debug handler to log all incoming updates"""
            try:
                if update.message:
                    message_type = "UNKNOWN"
                    if update.message.video:
                        message_type = "VIDEO"
                    elif update.message.document:
                        message_type = "DOCUMENT"
                    elif update.message.text:
                        message_type = "TEXT"
                    
                    username = update.message.from_user.username if update.message.from_user else "Unknown"
                    logger.info(f"Received message - Type: {message_type}, From: {username}, Content: {update.message.text if message_type == 'TEXT' else '[MEDIA]'}")
            except Exception as e:
                logger.error(f"Error in debug handler: {e}")
        
        # Add debug handler at a lower priority
        application.add_handler(MessageHandler(filters.ALL, debug_handler), group=999)
        
        # Register the error handler
        application.add_error_handler(error_handler)
        
        # Start the bot
        logger.info("Starting bot polling...")
        application.run_polling(
            drop_pending_updates=True,  # Don't process updates that occurred while bot was offline
            allowed_updates=Update.ALL_TYPES,  # Process all types of updates
            poll_interval=1.0,  # Check for updates every second
            timeout=30,  # Longer timeout for stability
        )
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
