import aiogram
import pymongo
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

bot = aiogram.Bot(token=os.getenv("PP_TOKEN"))
dp = aiogram.Dispatcher(bot, storage=MemoryStorage())

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['expenses_bot']
collection = db['expenses']


class BotStates(StatesGroup):
    CREATING_CATEGORY = State()
    SHOP_TITLE = State()
    DETAILS_CONFIRM = State()
    USER_INPUT_DETAILS = State()


@dp.message_handler(commands=['help'])
async def send_help(message: aiogram.types.Message):
    """
    Обработчик команды  /help.
    """
    await bot.send_message(message.from_user.id, "How can i help u?")


@dp.message_handler(commands=['start'])
async def send_welcome(message: aiogram.types.Message):
    """
    Обработчик команды /start
    """
    await bot.send_message(message.from_user.id, 'hi!')


@dp.message_handler(lambda message: message.text.lower() == "hello" or message.text.lower() == "hi",
                    content_types=['text'])
async def send_text(message: aiogram.types.Message):
    """
    Обработчтик текста. message содержит данные присланные пользователем в чат в виде текста и выполняет на основе
    текста определённые команды.
    """
    await bot.send_message(message.from_user.id, "Hi!")


@dp.message_handler(lambda message: message.text.lower() == "новые расходы", content_types=['text'], state='*')
async def start_creating_new_event(msg: aiogram.types.Message):
    """
    Обрабатываем сообщение о создании новых расходов
    """
    await bot.send_message(msg.from_user.id, "По какой категории?")
    await BotStates.CREATING_CATEGORY.set()


@dp.message_handler(content_types=['text'], state=BotStates.CREATING_CATEGORY)
async def expenses_title(message: aiogram.types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["category"] = message.text.lower()
        await BotStates.SHOP_TITLE.set()
        await bot.send_message(message.from_user.id, "Название магазина?")


@dp.message_handler(content_types=["text"], state=BotStates.SHOP_TITLE)
async def shop_title(message: aiogram.types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["shop"] = message.text.lower()
        await BotStates.DETAILS_CONFIRM.set()
        await bot.send_message(message.from_user.id, "Хотите указать детальную информацию о покупках?")


@dp.message_handler(lambda message: message.text.lower() == "да", content_types=['text'],
                    state=BotStates.DETAILS_CONFIRM)
async def details(message: aiogram.types.Message):
    await BotStates.USER_INPUT_DETAILS.set()
    await bot.send_message(message.from_user.id, "вводите \"название продукта: цена\"")


@dp.message_handler(content_types=["text"], state=BotStates.USER_INPUT_DETAILS)
async def user_input(message: aiogram.types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_data = str(message.text.lower()).split(':')


@dp.message_handler(lambda message: message.text.lower() == "отмена", content_types=["text"], state='*')
async def cancel_all(msg: aiogram.types.Message, state: FSMContext):
    """
    Обрабатываем сообщение отмены действия
    """
    await state.finish()
    await bot.send_message(msg.from_user.id, "Действие отменено")


if __name__ == '__main__':
    aiogram.executor.start_polling(dp)
