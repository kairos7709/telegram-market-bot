import json, os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")

DB_PATH = "bot_db.json"
UA = {"User-Agent": "Mozilla/5.0"}

def load_db():
    if not os.path.exists(DB_PATH):
        return {"chat_id": None}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_korea_indices():
    html = requests.get("https://finance.naver.com/sise/", headers=UA, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    kospi = soup.select_one("#KOSPI_now").text.strip()
    kosdaq = soup.select_one("#KOSDAQ_now").text.strip()
    return kospi, kosdaq

def get_usdkrw():
    html = requests.get("https://finance.naver.com/marketindex/", headers=UA, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    usdkrw = soup.select_one(".value").text.strip()
    return usdkrw

def make_message(title):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        kospi, kosdaq = get_korea_indices()
    except:
        kospi, kosdaq = "N/A", "N/A"
    try:
        usdkrw = get_usdkrw()
    except:
        usdkrw = "N/A"

    return (
        f"📌 {title}\n"
        f"⏰ {now}\n\n"
        f"📈 코스피: {kospi}\n"
        f"📉 코스닥: {kosdaq}\n"
        f"💵 달러/원: {usdkrw}\n"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    db["chat_id"] = update.effective_chat.id
    save_db(db)
    await update.message.reply_text("✅ 등록 완료! 이제 /today 를 치면 시황을 보내줄게.")

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = make_message("오늘의 국내 증시 시황")
    await update.message.reply_text(msg)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    print("🤖 봇 실행 중... 텔레그램에서 /today 해봐!")
    app.run_polling()

if __name__ == "__main__":
    main()

