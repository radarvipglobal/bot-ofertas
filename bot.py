import os
import sqlite3
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.environ.get("8695750211:AAHDfL-ik8tX4fuWev_WI66dX4-GlzARy0c")

AMAZON_ID = "radarvip01-20"
ALI_ID = "default"

PRODUCTOS_AR = [
    {"nombre": "🎣 Caña Kunnan Horizon", "link": "https://articulo.mercadolibre.com.ar/MLA-1714239051-cana-de-pesca-mosca-kunnan-horizon-_JM"},
    {"nombre": "🚗 Peugeot 207 Sedan", "link": "https://auto.mercadolibre.com.ar/MLA-3076197834-peugeot-207-14-sedan-active-75cv-_JM"},
]

PAISES = {"AR": "MLA", "CL": "MLC", "OTRO": "MLM"}

app_flask = Flask(__name__)

def db():
    return sqlite3.connect("bot.db")

def init_db():
    conn = db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, pais TEXT, consultas INT)")
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    data = c.fetchone()
    conn.close()
    return data

def save_user(user_id, pais):
    conn = db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)", (user_id, pais, 10))
    conn.commit()
    conn.close()

def update_consultas(user_id, n):
    conn = db()
    c = conn.cursor()
    c.execute("UPDATE users SET consultas=? WHERE id=?", (n, user_id))
    conn.commit()
    conn.close()

def amazon(q):
    return f"https://www.amazon.com/s?k={q}&tag={AMAZON_ID}"

def ali(q):
    return f"https://www.aliexpress.com/wholesale?SearchText={q}&aff_fcid={ALI_ID}"

def buscar_ml(site, q):
    url = f"https://api.mercadolibre.com/sites/{site}/search?q={q}"
    r = requests.get(url).json()
    if r.get("results"):
        item = r["results"][0]
        return f"{item['title']}\n💲 {item['price']}\n{item['permalink']}"
    return "No encontré resultados"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botones = [
        [InlineKeyboardButton("🇦🇷 Argentina", callback_data="AR")],
        [InlineKeyboardButton("🇨🇱 Chile", callback_data="CL")],
        [InlineKeyboardButton("🌎 Otro", callback_data="OTRO")]
    ]
    await update.message.reply_text("¿Desde qué país comprás?", reply_markup=InlineKeyboardMarkup(botones))

async def set_pais(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.callback_query.from_user.id)
    pais = update.callback_query.data
    save_user(user_id, pais)
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("¿Qué estás buscando?")

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = get_user(user_id)

    if not user:
        await update.message.reply_text("Escribí /start primero")
        return

    texto = update.message.text
    q = texto.replace(" ", "+")

    site = PAISES[user[1]]

    msg = "🔥 Resultado:\n\n"

    if user[1] == "AR":
        for p in PRODUCTOS_AR:
            msg += f"{p['nombre']}\n{p['link']}\n\n"

    msg += buscar_ml(site, q) + "\n\n"
    msg += amazon(q) + "\n\n"
    msg += ali(q)

    await update.message.reply_text(msg)

# TELEGRAM APP
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(set_pais))
app.add_handler(MessageHandler(filters.TEXT, buscar))

# WEBHOOK
@app_flask.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return "ok"

@app_flask.route("/")
def home():
    return "Bot activo"

if __name__ == "__main__":
    init_db()
    app.bot.set_webhook(url=os.environ.get("WEBHOOK_URL"))
    app_flask.run(host="0.0.0.0", port=8080)
