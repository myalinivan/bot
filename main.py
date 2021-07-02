import random
import re
import aiogram
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

bot = aiogram.Bot(token=os.getenv("PP_TOKEN"))
dp = aiogram.Dispatcher(bot, storage=MemoryStorage())


class CreateEvent(StatesGroup):
    WAITING_OF_TITLE = State()
    WAITING_OF_NOTICE_DATE = State()
    WAITING_OF_ALERT_TIME = State()


@dp.message_handler(commands=['help'])
async def send_help(message: aiogram.types.Message):
    """
    Обработчик команды  /help.
    """
    await bot.send_message(message.from_user.id, "How can i help u?")


@dp.message_handler(commands=['start'])
async def send_welcome(message: aiogram.types.Message):
    """
    Обработчик команды /help
    """
    await bot.send_message(message.from_user.id, 'hi!')


@dp.message_handler(lambda message: message.text.lower() == "hello", content_types=['text'])
async def send_text(message: aiogram.types.Message):
    """
    Обработчтик текста. message содержит данные присланные пользователем в чат в виде текста и выполняет на основе
    текста определённые команды.
    """
    await bot.send_message(message.from_user.id, "Hi!")


@dp.message_handler(lambda message: message.text.lower() == "новое событие", content_types=['text'], state='*')
async def start_creating_new_event(msg: aiogram.types.Message):
    await bot.send_message(msg.from_user.id, "Какое событие вы хотите создать?")
    await CreateEvent.WAITING_OF_TITLE.set()


@dp.message_handler(content_types=['text'], state=CreateEvent.WAITING_OF_TITLE)
async def event_created(message: aiogram.types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text.lower()
        rand_var = random.randint(1, 3)
        question = ""
        if rand_var == 1:
            question = "Когда будет это событие?"
        if rand_var == 2:
            question = "Введите дату события"
        if rand_var == 3:
            question = "Дата события?"
    await bot.send_message(message.from_user.id, question)
    await CreateEvent.next()


@dp.message_handler(content_types=['text'], state=CreateEvent.WAITING_OF_NOTICE_DATE)
async def create_notice_date(state: FSMContext, message: aiogram.types.Message):
    msg = re.search(r'[0-3][1-9]\.[0-1][0-9]\.')

if __name__ == '__main__':
    aiogram.executor.start_polling(dp)
