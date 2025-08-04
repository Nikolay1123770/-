
import json
import hashlib
import time
from aiogram import Bot, Dispatcher, types, executor
from config import BOT_TOKEN, FREEKASSA_ID, SECRET_1

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

PRICE = 100

def load_keys():
    with open("database.json", "r") as f:
        data = json.load(f)
    return data["keys"]

def save_keys(keys):
    with open("database.json", "w") as f:
        json.dump({"keys": keys}, f)

def generate_payment_link(user_id):
    order_id = f"{user_id}_{int(time.time())}"
    sign_str = f"{FREEKASSA_ID}:{PRICE}:{SECRET_1}:{order_id}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    url = f"https://pay.freekassa.ru/?m={FREEKASSA_ID}&oa={PRICE}&o={order_id}&s={sign}&us_user_id={user_id}"
    return url, order_id

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот для продажи ключей.\nНажми /buy, чтобы купить.")

@dp.message_handler(commands=['buy'])
async def buy(message: types.Message):
    link, order_id = generate_payment_link(message.from_user.id)
    await message.answer(f"Для оплаты перейди по ссылке:\n{link}\n\nПосле оплаты ключ будет выдан автоматически.")

@dp.message_handler(lambda message: message.text.startswith("check_order:"))
async def check_fake(message: types.Message):
    parts = message.text.split(":")
    if len(parts) != 2:
        await message.reply("Неверный формат.")
        return
    user_id = int(parts[1])
    keys = load_keys()
    if not keys:
        await bot.send_message(user_id, "Извините, ключи закончились.")
        return
    key = keys.pop(0)
    save_keys(keys)
    await bot.send_message(user_id, f"Спасибо за покупку! Ваш ключ: `{key}`", parse_mode="Markdown")

if __name__ == '__main__':
    executor.start_polling(dp)
