import logging
import requests
import os
import io
import base64
import json
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from google.cloud import speech
from google.cloud import translate_v2 as translate
import google.generativeai as genai
from PIL import Image # For creating placeholder images

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration ---
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_API_ENDPOINT = os.getenv("CHAT_API_ENDPOINT")
IMAGE_EDIT_ENDPOINT = os.getenv("IMAGE_EDIT_ENDPOINT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- State Definitions ---
SELECTING_LANGUAGE, SELECTING_ACTION, AWAITING_ONBOARDING_ID, ONBOARDING_QUESTIONS, \
STORY_AWAITING_USER_ID, STORY_AWAITING_PRODUCT, STORY_AWAITING_HISTORY, \
STORY_AWAITING_MAKING, STORY_AWAITING_ARTISAN = range(9)


# --- Translation & Reply Helpers ---

def translate_text(text: str, target_language: str) -> str:
    # (Translation logic remains the same)
    if not text or target_language == 'en': return text
    try:
        translate_client = translate.Client()
        result = translate_client.translate(text, target_language=target_language)
        return result['translatedText']
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        return text

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, **kwargs):
    # (Reply logic remains the same)
    target_language = context.user_data.get('target_language', 'en')
    translated_text = translate_text(text, target_language)
    await update.message.reply_text(translated_text, **kwargs)


# --- Voice Transcription ---
async def transcribe_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    # (Voice transcription logic remains the same)
    if not update.message.voice: return None
    try:
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        content = await voice_file.download_as_bytearray()
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=bytes(content))
        language_code = context.user_data.get('language_code', 'en-US')
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,
            language_code=language_code,
        )
        await reply(update, context, "Processing your voice message...")
        response = client.recognize(config=config, audio=audio)
        if response.results and response.results[0].alternatives:
            return response.results[0].alternatives[0].transcript
        await reply(update, context, "Sorry, I couldn't understand the audio.")
        return None
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        await reply(update, context, "Sorry, there was an error processing your voice message.")
        return None

# --- Storybook Generation Logic ---

async def generate_storybook_text(story_inputs: dict, update: Update, context: ContextTypes.DEFAULT_TYPE) -> list | None:
    """Generates the 7-page story text using the Gemini API."""
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured.")
        await reply(update, context, "Story generation is not configured. Please contact an admin.")
        return None
        
    await reply(update, context, "I have all the details. Now, I'm writing your story...")
    
    # This prompt is adapted from your main.py
    prompt = f"""
You are a storybook generator. Create a 7-page storybook and return ONLY valid JSON.
Page Flow: Pages 1-2: History, Pages 3-4: Making, Pages 5-6: Artisan, Page 7: Closure.
For each page, output story_text (2–3 sentences, oral-tale style).
Return ONLY this JSON format: {{"pages": [{{"section": "History", "page": 1, "story_text": "your narration"}}]}}

Product: {story_inputs.get("product")}
History: {story_inputs.get("history")}
Making Process: {story_inputs.get("making")}
About Artisan: {story_inputs.get("artisan")}
"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async(prompt)
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        story_data = json.loads(response_text)
        logger.info("Successfully generated storybook text from Gemini.")
        return story_data.get("pages", [])
    except Exception as e:
        logger.error(f"Error calling Gemini API for story text: {e}", exc_info=True)
        await reply(update, context, "I'm sorry, I had trouble writing the story. Please try again.")
        return None

def create_placeholder_image() -> bytes:
    """Creates a simple 1x1 white pixel PNG to send to the API."""
    img = Image.new('RGB', (1, 1), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

async def generate_storybook_image(page: dict, user_id: str) -> bytes | None:
    """Generates a single image for a story page using the backend API."""
    if not IMAGE_EDIT_ENDPOINT:
        logger.error("IMAGE_EDIT_ENDPOINT is not configured.")
        return None
        
    # This prompt logic is adapted from your imagen.py
    base_style = "Indian folk-art style like Krish Trish Baltiboy, earthy bright tones, quirky expressions, patterned motifs (tree, sun, river, huts, borders), simplified illustrations"
    section = page.get("section")
    story_text = page.get("story_text")

    if section == "History": scene = f"Ancient Indian village scene depicting: {story_text}"
    elif section == "Making": scene = f"Artisan crafting process showing: {story_text}"
    elif section == "Artisan": scene = f"Portrait of artisan and family depicting: {story_text}"
    else: scene = f"Panoramic mural combining all elements: {story_text}"
    
    prompt = f"{scene}. {base_style}. Continuation of previous scene, same artisan character."
    
    try:
        files = {'image': ('placeholder.png', create_placeholder_image(), 'image/png')}
        data = {'user_id': user_id, 'prompt': prompt}
        response = requests.post(IMAGE_EDIT_ENDPOINT, files=files, data=data)
        response.raise_for_status()
        base64_image = response.json().get("image_base64")
        if base64_image:
            return base64.b64decode(base64_image)
        return None
    except Exception as e:
        logger.error(f"Error generating image for page {page.get('page')}: {e}")
        return None

# --- Main Bot Conversation Flows ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # (Start logic remains the same)
    reply_keyboard = [["English", "हिंदी (Hindi)"]]
    await update.message.reply_text("Welcome! Please select your language.\n\nकृपया अपनी भाषा चुनें।",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SELECTING_LANGUAGE

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # (Language selection logic remains the same)
    choice = update.message.text
    if "English" in choice or "english" in choice.lower():
        context.user_data.update({'language_code': 'en-US', 'target_language': 'en'})
    elif "हिंदी" in choice or "hindi" in choice.lower():
        context.user_data.update({'language_code': 'hi-IN', 'target_language': 'hi'})
    else:
        await update.message.reply_text("Please select a valid language.")
        return SELECTING_LANGUAGE

    reply_keyboard = [["Complete Onboarding Form"], ["Create a Storybook"]]
    await reply(update, context, "Great! What would you like to do?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SELECTING_ACTION

async def handle_action_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # (Action selection logic updated for Storybook)
    user_choice = update.message.text
    if "Onboarding Form" in user_choice:
        await reply(update, context, "Starting onboarding. First, please provide your User ID.", reply_markup=ReplyKeyboardRemove())
        return AWAITING_ONBOARDING_ID
    elif "Create a Storybook" in user_choice:
        await reply(update, context, "Let's create a story! First, please provide your User ID.", reply_markup=ReplyKeyboardRemove())
        return STORY_AWAITING_USER_ID
    else:
        await reply(update, context, "Sorry, I didn't understand that. Please choose an option.")
        return SELECTING_ACTION

# --- Onboarding Flow (Unchanged) ---
async def get_onboarding_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (This function remains unchanged)
    context.user_data['onboarding_user_id'] = update.message.text
    api_payload = {"message": f"Start onboarding for user_id: {update.message.text}", "user_id": update.message.text}
    try:
        response = requests.post(CHAT_API_ENDPOINT, json=api_payload)
        response.raise_for_status()
        question = response.json().get("response", "Error getting first question.")
        context.user_data['last_question'] = question
        await reply(update, context, question)
        return ONBOARDING_QUESTIONS
    except requests.RequestException as e:
        logger.error(f"API request error: {e}")
        await reply(update, context, "Could not start onboarding. Please /cancel and try again.")
        return ConversationHandler.END

async def handle_onboarding_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (This function remains unchanged)
    answer = update.message.text or await transcribe_voice(update, context)
    if not answer:
        if last_question := context.user_data.get('last_question'):
            await reply(update, context, "Let's try that again.\n\n" + last_question)
        return ONBOARDING_QUESTIONS
    
    user_id = context.user_data.get('onboarding_user_id')
    api_payload = {"message": answer, "user_id": user_id}
    try:
        response = requests.post(CHAT_API_ENDPOINT, json=api_payload)
        response.raise_for_status()
        api_response = response.json()
        next_question = api_response.get("response")
        if not api_response.get("is_onboarding", True):
            await reply(update, context, next_question + "\n\nOnboarding complete!")
            context.user_data.clear()
            return ConversationHandler.END
        else:
            context.user_data['last_question'] = next_question
            await reply(update, context, next_question)
            return ONBOARDING_QUESTIONS
    except requests.RequestException as e:
        logger.error(f"API request error: {e}")
        await reply(update, context, "Error processing your answer. Please /cancel and try again.")
        return ConversationHandler.END


# --- New Storybook Creation Flow ---
async def get_storybook_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['story_user_id'] = update.message.text
    context.user_data['story_inputs'] = {}
    await reply(update, context, "Thank you. First, what is the name of the product or craft? (e.g., 'clay pot', 'Madhubani painting')")
    return STORY_AWAITING_PRODUCT

async def get_storybook_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text or await transcribe_voice(update, context)
    if not answer: return STORY_AWAITING_PRODUCT
    context.user_data['story_inputs']['product'] = answer
    await reply(update, context, "Got it. Now, tell me about the history of this craft. Where did it come from?")
    return STORY_AWAITING_HISTORY

async def get_storybook_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text or await transcribe_voice(update, context)
    if not answer: return STORY_AWAITING_HISTORY
    context.user_data['story_inputs']['history'] = answer
    await reply(update, context, "Wonderful. Next, briefly describe how it's made.")
    return STORY_AWAITING_MAKING

async def get_storybook_making(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text or await transcribe_voice(update, context)
    if not answer: return STORY_AWAITING_MAKING
    context.user_data['story_inputs']['making'] = answer
    await reply(update, context, "Almost done. Finally, tell me about the artisan or the family who makes it.")
    return STORY_AWAITING_ARTISAN

async def get_storybook_artisan_and_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the final piece of info, then generates the full storybook with images."""
    answer = update.message.text or await transcribe_voice(update, context)
    if not answer: return STORY_AWAITING_ARTISAN
    context.user_data['story_inputs']['artisan'] = answer

    # --- Generation Starts ---
    story_pages = await generate_storybook_text(context.user_data['story_inputs'], update, context)

    if story_pages:
        await reply(update, context, "Story complete! Now, I will create the illustrations for each page. This might take a few minutes.")
        user_id = context.user_data['story_user_id']
        
        for page in story_pages:
            page_num = page.get('page')
            story_text = page.get('story_text')
            
            await reply(update, context, f"Generating image for page {page_num}...")
            image_bytes = await generate_storybook_image(page, user_id)
            
            translated_story_text = translate_text(story_text, context.user_data.get('target_language', 'en'))

            if image_bytes:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=image_bytes,
                    caption=f"Page {page_num}:\n\n{translated_story_text}"
                )
            else:
                await reply(update, context, f"Page {page_num}:\n\n{story_text}\n\n(I couldn't create an image for this page.)")
        
        await reply(update, context, "Your storybook is complete!")
    
    context.user_data.clear()
    return ConversationHandler.END

# --- General ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await reply(update, context, "Process canceled. Type /start to begin again.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    """Main function for running bot standalone (not used in Docker)"""
    if not all([TELEGRAM_BOT_TOKEN, CHAT_API_ENDPOINT, IMAGE_EDIT_ENDPOINT, GEMINI_API_KEY, os.getenv("GOOGLE_APPLICATION_CREDENTIALS")]):
        logger.error("FATAL: One or more required environment variables are missing.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_LANGUAGE: [MessageHandler(filters.Regex("^(English|हिंदी \(Hindi\)|english|hindi)$"), handle_language_selection)],
            SELECTING_ACTION: [MessageHandler(filters.Regex("^(Complete Onboarding Form|Create a Storybook)$"), handle_action_selection)],
            # Onboarding States
            AWAITING_ONBOARDING_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_onboarding_id)],
            ONBOARDING_QUESTIONS: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, handle_onboarding_questions)],
            # Storybook States
            STORY_AWAITING_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_storybook_user_id)],
            STORY_AWAITING_PRODUCT: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, get_storybook_product)],
            STORY_AWAITING_HISTORY: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, get_storybook_history)],
            STORY_AWAITING_MAKING: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, get_storybook_making)],
            STORY_AWAITING_ARTISAN: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, get_storybook_artisan_and_generate)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    print("Bot is running with Storybook generation support...")
    application.run_polling()

# --- FastAPI Health App ---
from fastapi import FastAPI
import uvicorn
import asyncio

health_app = FastAPI()

@health_app.get("/health")
def healthcheck():
    return {"status": "ok"}

# --- Start Telegram bot polling on FastAPI startup ---
_bot_app = None  # python-telegram-bot Application

def _build_bot_app():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_LANGUAGE: [MessageHandler(filters.Regex("^(English|हिंदी \(Hindi\)|english|hindi)$"), handle_language_selection)],
            SELECTING_ACTION: [MessageHandler(filters.Regex("^(Complete Onboarding Form|Create a Storybook)$"), handle_action_selection)],
            AWAITING_ONBOARDING_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_onboarding_id)],
            ONBOARDING_QUESTIONS: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, handle_onboarding_questions)],
            STORY_AWAITING_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_storybook_user_id)],
            STORY_AWAITING_PRODUCT: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, get_storybook_product)],
            STORY_AWAITING_HISTORY: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, get_storybook_history)],
            STORY_AWAITING_MAKING: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, get_storybook_making)],
            STORY_AWAITING_ARTISAN: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, get_storybook_artisan_and_generate)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    return application

@health_app.on_event("startup")
async def _start_bot():
    global _bot_app
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing; bot will not start.")
        return
    try:
        _bot_app = _build_bot_app()
        await _bot_app.initialize()
        await _bot_app.start()
        # Start polling in background without blocking
        asyncio.create_task(_bot_app.updater.start_polling())
        logger.info("Telegram bot started successfully")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}", exc_info=True)

@health_app.on_event("shutdown")
async def _stop_bot():
    global _bot_app
    if _bot_app:
        try:
            await _bot_app.updater.stop()
            await _bot_app.stop()
            await _bot_app.shutdown()
            logger.info("Telegram bot stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {e}", exc_info=True)

if __name__ == "__main__":
    main()

# To run: uvicorn main:health_app --host 0.0.0.0 --port 8080

