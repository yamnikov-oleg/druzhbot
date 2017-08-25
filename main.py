#!/usr/bin/env python3
import logging
import random
import sys
from functools import wraps
from typing import List, Callable, Any

from telegram import Bot, Update, InlineQueryResultCachedSticker
from telegram.ext import Updater, MessageHandler, InlineQueryHandler, Filters

import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def into_words(q: str) -> List[str]:
    # Remove all syntax symbols
    syntax_marks = ",.!?-"
    for sym in syntax_marks:
        q = q.replace(sym, ' ')

    # Split into words
    words = q.lower().strip().split()
    words = [w.strip() for w in words]
    words = [w for w in words if w]

    return words


def word_in_words(word: str, words: List[str]) -> bool:
    for w in words:
        if w.startswith(word):
            return True
    return False


def search_stickers(query: str) -> List[str]:
    query_words = into_words(query)

    stickers = []
    for file_id, texts in config.STICKERS.items():
        texts_string = " ".join(texts).lower()
        texts_words = into_words(texts_string)
        if all([ word_in_words(w, texts_words) for w in query_words ]):
            stickers.append(file_id)

    return stickers


def random_stickers(n: int) -> List[str]:
    ids = list(config.STICKERS.keys())
    random.shuffle(ids)
    return ids[:n]


def log_exceptions(f: Callable[[Any], Any]):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error("{} on {}: {}".format(type(e).__qualname__, f.__name__, str(e)))
    return wrapper


@log_exceptions
def on_query(bot: Bot, update: Update):
    # This constant is defined by the Bot API.
    MAX_RESULTS = 50

    inline_query = update.inline_query

    if not inline_query:
        return

    # If query is empty - return random stickers.
    return_random = not inline_query.query

    logger.info("Inline query from {}:{} with text '{}'".format(
        inline_query.from_user.id, inline_query.from_user.first_name,
        inline_query.query))

    if return_random:
        stickers = random_stickers(MAX_RESULTS)
    else:
        stickers = search_stickers(inline_query.query)

    if len(stickers) > MAX_RESULTS:
        stickers = stickers[:MAX_RESULTS]

    results = [InlineQueryResultCachedSticker(fid, fid) for fid in stickers]

    cache_time = 600
    if return_random:
        # Do not cache random results.
        cache_time = 0

    bot.answer_inline_query(inline_query.id, results, cache_time=cache_time)


@log_exceptions
def on_message(bot: Bot, update: Update):
    message = update.message

    if not message:
        return

    is_sticker = bool(message.sticker)
    sticker_is_in_db = is_sticker and message.sticker.file_id in config.STICKERS

    if sticker_is_in_db:
        logger.info("Message from {}:{} with known sticker '{}'".format(
            message.from_user.id, message.from_user.first_name,
            message.sticker.file_id))
        bot.send_message(
            message.chat.id,
            config.HYPE_MSG,
            parse_mode='Markdown')
    elif is_sticker:
        logger.info("Message from {}:{} with unknown sticker '{}'".format(
            message.from_user.id, message.from_user.first_name,
            message.sticker.file_id))
        bot.send_message(
            message.chat.id,
            config.STICKER_DATA_MSG.format(file_id=message.sticker.file_id),
            parse_mode='Markdown')
    else:
        logger.info("Message from {}:{} with text '{}'".format(
            message.from_user.id, message.from_user.first_name, message.text))
        bot.send_message(
            message.chat.id,
            config.INSTRUCTIONS_MSG.format(stickers_count=len(config.STICKERS)),
            parse_mode='Markdown')


def main():
    if not config.TELEGRAM_BOT_KEY:
        raise RuntimeError("Please, put you bot api key into the config.")

    logger.info("Stickers in the DB: {}".format(len(config.STICKERS)))

    updater = Updater(token=config.TELEGRAM_BOT_KEY)
    dispatcher = updater.dispatcher

    query_handler = InlineQueryHandler(on_query)
    dispatcher.add_handler(query_handler)

    msg_handler = MessageHandler(Filters.all, on_message)
    dispatcher.add_handler(msg_handler)

    if config.ENABLE_WEBHOOK:
        logger.info("Starting druzhbot webhook at {}...".format(config.WEBHOOK_URL))
        updater.start_webhook(
            listen='0.0.0.0',
            port=config.WEBHOOK_PORT,
            webhook_url=config.WEBHOOK_URL,
            cert=config.WEBHOOK_CERT,
            key=config.WEBHOOK_CERT_KEY)
        updater.bot.set_webhook(config.WEBHOOK_URL)
    else:
        logger.info("Starting druzhbot polling...")
        updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
