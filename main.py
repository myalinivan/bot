import random
import aiogram
import pymongo
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

bot = aiogram.Bot(token=os.getenv("PP_TOKEN"))
dp = aiogram.Dispatcher(bot, storage=MemoryStorage())

client = pymongo.MongoClient('127.0.0.1', '27017')
db = client['expenses_bot']
collection = db['expenses']

class CreateEvent(StatesGroup):
    CATEGORY_SET = State()
    CREATING_CATEGORY = State()


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


@dp.message_handler(lambda message: message.text.lower() == "hello" or message.text.lower() == "Hi", content_types=['text'])
async def send_text(message: aiogram.types.Message):
    """
    Обработчтик текста. message содержит данные присланные пользователем в чат в виде текста и выполняет на основе
    текста определённые команды.
    """
    await bot.send_message(message.from_user.id, "Hi!")


@dp.message_handler(lambda message: message.text.lower() == "новые расходы", content_types=['text'], state='*')
async def start_creating_new_event(msg: aiogram.types.Message):
    await bot.send_message(msg.from_user.id, "По какой категории?")
    await CreateEvent.CATEGORY_SET.set()


@dp.message_handler(lambda message: message.text.lower() == "новая категория", content_types=['text'], state=CreateEvent.CATEGORY_SET)
async def event_created(msg: aiogram.types.Message):
    await bot.send_message(msg.from_user.id, "Имя новой категории?")
    await CreateEvent.CREATING_CATEGORY.set()


@dp.message_handler(content_types=['text'], state=CreateEvent.CREATING_CATEGORY)
async def new_category(msg: aiogram.types.Message, state: FSMContext):
    async with state.proxy() as Data:
        Data['new category'] = msg.text.lower()
        collection[str(msg.from_user.id)]['categories'] = str(Data['new category'])
        await bot.send_message(msg.from_user.id, 'Новая категория создана')
        await bot.send_message(msg.from_user.id, "Продолжить выбор категории?")


@dp.message_handler(lambda message: message.text.lower() == "да", content_types=['text'], state=CreateEvent.CREATING_CATEGORY, )
async def setting_category(msg: aiogram.types.Message):
    await CreateEvent.CATEGORY_SET.set()
    await bot.send_message(msg.from_user.id, "Какую категорию расходов вы хотите выбрать?")


@dp.message_handler(lambda message: message.text.lower() == "нет", content_types=['text'], state=CreateEvent.CREATING_CATEGORY, )
async def setting_category(state: FSMContext):
    await state.finish()

if __name__ == '__main__':
    aiogram.executor.start_polling(dp)
