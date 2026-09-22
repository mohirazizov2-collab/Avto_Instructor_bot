import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("BOT_TOKEN")

if not token:
    print("❌ BOT_TOKEN topilmadi!")
    exit()

webhook_url = "https://avtomaktab-bot.vercel.app/api/webhook"

url = f"https://api.telegram.org/bot{token}/setWebhook"

response = requests.post(
    url,
    json={"url": webhook_url}
)

print(response.json())