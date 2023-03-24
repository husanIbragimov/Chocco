from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

bot = Bot(token='5978476855:AAEUfYUTXPDGQsjLzGBmuf21fbz3hgKje7k')
url = 'http://127.0.0.1:8000/'
url_server = 'http://choko.uz/'
dp = Dispatcher(bot)

categoryMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Qabul qilish", callback_data="Complated"),
            InlineKeyboardButton(text="❌ Qaytarish", callback_data="Censel"),
        ],
    ])


async def order_product(data):
    User = data[0]['user']
    photo1 = url_server + data[0]['photo']
    #photo1 = "http://choko.uz/media/products/Apple_iPhone_14_Pro_%D1%81%D0%B5%D1%80%D0%B5%D0%B1%D1%80%D0%B8%D1%81%D1%82%D1%8B%D0%B9_1_gHZ9MhM.jpg"
    text = f"<b>Yangi Buyurtma</b> \n" \
           f"Telefon raqam: {User} \n" \

    for i in data:
        text += f"------------------------\n" \
                f"Product: {i['product']} \n" \
                f"Muddat: {i['variant']} oyga\n"

    await  bot.send_photo(chat_id='739412274', photo=photo1, reply_markup=categoryMenu,
                          caption=text, parse_mode='html')
