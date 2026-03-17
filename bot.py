import os
import telebot

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# guardar pais del usuario
usuarios = {}

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "¿De qué país sos?\n1- Argentina\n2- Chile\n3- México")

@bot.message_handler(func=lambda m: True)
def responder(msg):
    texto = msg.text.lower()
    user_id = msg.chat.id

    # detectar país
    if texto in ["1", "argentina"]:
        usuarios[user_id] = "AR"
        bot.send_message(user_id, "Listo 🇦🇷 Ahora buscá lo que quieras")
        return
    elif texto in ["2", "chile"]:
        usuarios[user_id] = "CL"
        bot.send_message(user_id, "Listo 🇨🇱 Ahora buscá lo que quieras")
        return
    elif texto in ["3", "mexico"]:
        usuarios[user_id] = "MX"
        bot.send_message(user_id, "Listo 🇲🇽 Ahora buscá lo que quieras")
        return

    pais = usuarios.get(user_id)

    if not pais:
        bot.send_message(user_id, "Primero decime tu país con /start")
        return

    # RESPUESTA SIMPLE (luego mejoramos)
    if pais == "AR":
        bot.send_message(user_id, f"Buscando en Argentina...\nResultado ML + Amazon + AliExpress para: {texto}")
    elif pais == "CL":
        bot.send_message(user_id, f"Buscando en Chile...\nResultado ML + Amazon + AliExpress para: {texto}")
    elif pais == "MX":
        bot.send_message(user_id, f"Buscando en México...\nResultado Amazon + AliExpress para: {texto}")

bot.polling()
