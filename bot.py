import settings
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN
OPENAI_API_KEY = settings.OPEN_API_KEY

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

async def classify_topic(question: str) -> bool:
    """
    Проверяет, относится ли вопрос к боксу через OpenAI.
    Возвращает True, если вопрос по боксу.
    """
    classification_prompt = f"""
Ты классификатор тем. Определи, относится ли вопрос к боксу.
Под "боксом" понимаются:
- профессиональный или любительский бокс
- техника ударов, защита, стратегия
- тренировки, бойцы, промоушены, история бокса
- экипировка, судейство, категории, тренеры и т.п.

Если вопрос не о боксе (например про ММА, карате, футбол, политику, психологию, жизнь, отношения и т.д.) — это НЕ бокс.

Ответь СТРОГО одним словом: "ДА" или "НЕТ".

Вопрос: "{question}"
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "Ты классификатор. Отвечай только 'ДА' или 'НЕТ'."},
            {"role": "user", "content": classification_prompt}
        ]
    )

    answer = response.choices[0].message.content.strip().upper()
    return answer == "ДА"

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("🥊 Привет! Я ИИ-тренер по боксу. Задай мне вопрос о боксе!")

@dp.message()
async def handle_message(message: Message):
    user_input = message.text.strip()

    is_boxing = await asyncio.to_thread(classify_topic, user_input)

    if not is_boxing:
        await message.answer("Я отвечаю только на вопросы, связанные с **боксом** 🥊")
        return

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        messages=[
            {"role": "system", "content": (
                "Ты эксперт по боксу. Отвечай профессионально, но понятно. "
                "Если вопрос не относится к боксу, ты должен ответить только: "
                "'Я отвечаю только на вопросы, связанные с боксом 🥊'."
            )},
            {"role": "user", "content": user_input}
        ]
    )

    answer = response.choices[0].message.content.strip()
    await message.answer(answer)

async def main():
    print("🤖 Бот запущен и готов анализировать темы...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())