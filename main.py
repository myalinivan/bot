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


class CreateEvent(StatesGroup):
    CATEGORY_SET = State()
    CREATING_CATEGORY = State()
    CATEGORY_CREATED = State()


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
    await CreateEvent.CREATING_CATEGORY.set()


@dp.message_handler(lambda message: message.text.lower() == "отмена", content_types=["text"], state='*')
async def cancel_all(msg: aiogram.types.Message, state: FSMContext):
    """
    Обрабатываем сообщение отмены действия
    """
    await state.finish()
    await bot.send_message(msg.from_user.id, "Действие отменено")


@dp.message_handler(lambda message: message.text.lower() == "новая категория", content_types=['text'], state="*")
async def event_created(msg: aiogram.types.Message):
    """
    Обрабатываем сообщение "новая категория".
    """
    await bot.send_message(msg.from_user.id, "Имя новой категории?")
    await CreateEvent.CREATING_CATEGORY.set()


@dp.message_handler(content_types=['text'], state=CreateEvent.CREATING_CATEGORY)
async def new_category(msg: aiogram.types.Message, state: FSMContext):
    """
    Данный обработчик текста реагирует на любое последующее сообщение. И записывает и сразу посылает в БД
    название новой категории. Состояние не меняется.
    """
    async with state.proxy() as data:
        data['new category'] = msg.text.lower()
        if collection.count_documents({"user_id": str(msg.from_user.id)}) != 0:
            # Подсчитываем количество пользователей для понимания существуют ли вообще запись
            if collection.count_documents({"user_id": str(msg.from_user.id),
                                           "categories:": {"category": data["new category"]}}) == 0:
                # Подсчитываем количество категорий с таким же именем для понмания существует ли вообще такая категория
                # Если нет - то создаём запись к существующему пользователю
                category = {
                    "category": data["new category"],
                    "expenses": {}
                }
                collection["categories"].insert_one(category)
                await bot.send_message(msg.from_user.id, 'Новая категория создана')
                await CreateEvent.CATEGORY_CREATED.set()
                await bot.send_message(msg.from_user.id, "Начать выбор категории?")
            else:
                await bot.send_message(msg.from_user.id, "Эта категория существует!")
                return


@dp.message_handler(lambda message: message.text.lower() == "да", content_types=['text'],
                    state=CreateEvent.CATEGORY_CREATED)
async def setting_category(msg: aiogram.types.Message, state: FSMContext):
    """
    При ответе "да" на вопрос о продолжении создания новой категории выставляем состояние "Category_set"
    """
    await state.finish()
    await CreateEvent.CATEGORY_SET.set()
    await bot.send_message(msg.from_user.id, "Какую категорию расходов вы хотите выбрать?")


@dp.message_handler(lambda message: message.text.lower() == "нет", content_types=['text'],
                    state=CreateEvent.CATEGORY_CREATED)
async def finish_setting_category(msg: aiogram.types.Message, state: FSMContext):
    """
    При ответе "нет" на вопрос о продолжении создания категории сбрасываем состояние
    """
    await state.finish()
    await bot.send_message(msg.from_user.id, "Выбор категории отменён")

if __name__ == '__main__':
    aiogram.executor.start_polling(dp)
