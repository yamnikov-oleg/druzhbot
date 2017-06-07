# Please, insert your bot api key, provided by the BotFather.
TELEGRAM_BOT_KEY = ""

INSTRUCTIONS_MSG="""
Привет! Я инлайновый бот, который поможет тебе найти стикеры с самыми хайповыми цитатами Сергея Дружко.

Чтобы использовать меня, введи в любом чате мое имя @druzhbot, затем начало цитаты, и я пришлю тебе стикеры, которые найду.

К сожалению, больше мне сказать нечего. Это все, чему меня научили.
""".strip()

STICKER_DATA_MSG="""
File ID: `{file_id}`

Это секретная информация для разработчиков. Если ты не разработчик, никому не говорил, что ты видел!
""".strip()

# This is the "data base" of searched stickers.
# Keys are the file ids of the stickers. Values are arrays of searchable texts.
#
# To get file id of an arbitrary sticker, just send it to the bot.
STICKERS = {
    'CAADAgADFQYAAgi3GQInJ_dji2gMHwI': [
        "you know nothing jon snow",
        "ничего ты не знаешь джон сноу",
    ]
}
