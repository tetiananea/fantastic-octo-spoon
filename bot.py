import requests
import time
import json
from datetime import datetime

TOKEN = "8035722401:AAEg-h6jNzz7KSJB_ACzhM82KE4EPpztKa0"  # ← ТВОЙ ТОКЕН ИЗ @BotFather
URL = f"https://api.telegram.org/bot{TOKEN}"

# Загружаем 484 прогноза
with open('forecasts.json', 'r', encoding='utf-8') as f:
    FORECASTS = json.load(f)

ARCANA_NAMES = {1: "Маг", 2: "Жрица", 3: "Императрица", 4: "Император", 5: "Иерофант",
                6: "Влюблённые", 7: "Колесница", 8: "Справедливость", 9: "Отшельник",
                10: "Колесо", 11: "Сила", 12: "Повешенный", 13: "Смерть", 14: "Умеренность",
                15: "Дьявол", 16: "Башня", 17: "Звезда", 18: "Луна", 19: "Солнце",
                20: "Суд", 21: "Мир", 22: "Мир"}

def get_arcana(d, m, y):
    s = d + m + y
    while s > 22:
        s = sum(int(x) for x in str(s))
    return s if s != 0 else 22

def send(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if keyboard:
        data["reply_markup"] = keyboard
    requests.post(f"{URL}/sendMessage", json=data)

offset = 0
print("БОТ ЗАПУЩЕН! С 484 прогнозами")

while True:
    try:
        res = requests.get(f"{URL}/getUpdates", params={"offset": offset, "timeout": 30}).json()
        for upd in res.get("result", []):
            offset = upd["update_id"] + 1
            if "message" in upd:
                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")

                if text == "/start":
                    kb = {"inline_keyboard": [
                        [{"text": "Бесплатный расчёт", "callback_data": "free"}],
                        [{"text": "Подписка — 5 Stars/мес", "callback_data": "sub"}],
                        [{"text": "Матрица — 30$", "callback_data": "full"}]
                    ]}
                    send(chat_id, "*Matrix Fate Bot*\n\nВыбери:", kb)

                elif len(text) == 10 and "." in text:
                    try:
                        d, m, y = map(int, text.split('.'))
                        personal = get_arcana(d, m, y)
                        day_arc = get_arcana(datetime.now().day, datetime.now().month, datetime.now().year)
                        forecast = FORECASTS.get(str(personal), {}).get(str(day_arc), "Общий совет: Гармонизируй энергии.")
                        send(chat_id, f"*Дата:* {text}\n*Твой аркан:* {personal} — {ARCANA_NAMES[personal]}\n*Аркан дня:* {day_arc} — {ARCANA_NAMES[day_arc]}\n\n*{forecast}*")
                    except:
                        send(chat_id, "Ошибка! Пример: 10.07.1974")

            elif "callback_query" in upd:
                cb = upd["callback_query"]
                chat_id = cb["message"]["chat"]["id"]
                data = cb["data"]
                if data == "free":
                    send(chat_id, "Введи дату: *ДД.ММ.ГГГГ*")
                elif data == "sub":
                    send(chat_id, "Подписка: 5 Stars/мес", {"inline_keyboard": [[{"text": "Оплатить", "pay": True}]]})
                elif data == "full":
                    send(chat_id, "Матрица: 30$", {"inline_keyboard": [[{"text": "Оплатить", "pay": True}]]})
                requests.post(f"{URL}/answerCallbackQuery", {"callback_query_id": cb["id"]})

    except Exception as e:
        print("Ошибка:", e)
    time.sleep(1)
