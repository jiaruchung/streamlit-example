import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Print debug output
print("[DEBUG] OPENAI_API_KEY loaded:", bool(os.getenv("OPENAI_API_KEY")))
print("[DEBUG] GMAIL_APP_PASSWORD loaded:", bool(os.getenv("GMAIL_APP_PASSWORD")))
print("[DEBUG] STRIPE_SECRET_KEY loaded:", bool(os.getenv("STRIPE_SECRET_KEY")))
print("[DEBUG] STRIPE_WEBHOOK_SECRET loaded:", bool(os.getenv("STRIPE_WEBHOOK_SECRET")))
print("[DEBUG] SENDER_EMAIL loaded:", os.getenv("SENDER_EMAIL"))
