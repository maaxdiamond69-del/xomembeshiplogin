from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from playwright.async_api import async_playwright

# ==========================
# CONFIG
# ==========================
import os

BOT_TOKEN = os.getenv("8934081604:AAE3psqa1S8sbvOHnGlnm2i_u9NcHTGwzJ4")
WEBSITE = "https://version-common-redflamenco.vercel.app/"

# ==========================
# SAVE VERIFIED TOKENS
# ==========================

def save_successful_token(token):
    with open("verified_tokens.txt", "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {token}\n"
        )

# ==========================
# VERIFY TOKEN
# ==========================

async def verify_token(token: str):
    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = await browser.new_page()

        try:
            await page.goto(
                WEBSITE,
                wait_until="networkidle",
                timeout=30000
            )

            # Enter token
            await page.locator("input").fill(token)

            # Click Verify Token
            await page.get_by_role(
                "button",
                name="Verify Token"
            ).click()

            # Wait for result
            await page.wait_for_timeout(3000)

            # Read page
            result = await page.locator("body").inner_text()

            await browser.close()

            return result

        except Exception:

            try:
                await browser.close()
            except:
                pass

            return "API_NOT_RESPONDING"

# ==========================
# HANDLE MESSAGE
# ==========================

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    token = update.message.text.strip()

    if len(token) != 64:
        await update.message.reply_text(
            "❌ Please send a valid 64-character token."
        )
        return

    waiting = await update.message.reply_text(
        "🔄 Connecting to System..."
    )

    result = await verify_token(token)

    if result == "API_NOT_RESPONDING":

        text = (
            "⚠️ <b>System Busy</b>\n\n"
            "🔄  not responding.\n"
            "Please try again later."
        )

    elif (
        "Connected" in result
        or "Token verified" in result
        or "Verified" in result
    ):

        # Save only successful tokens
        save_successful_token(token)

        text = (
            "🟢 <b>Connected to System</b>\n\n"
            "✅ Token Verified Successfully\n"
            "🔐 Secure Connection Established\n"
            "🚀 Access Granted"
        )

    else:

        text = (
            "🔴 <b>Connection Failed</b>\n\n"
            "❌ Invalid or Expired Token"
        )

    await waiting.edit_text(
        text,
        parse_mode="HTML"
    )

# ==========================
# MAIN
# ==========================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle,
        )
    )

    print("Bot Started...")

    app.run_polling()

if __name__ == "__main__":
    main()
