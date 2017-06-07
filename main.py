#!/usr/bin/env python3
from typing import List

from telegram import Bot, Update, InlineQueryResultCachedSticker
from telegram.ext import Updater, MessageHandler, InlineQueryHandler, Filters

import config


def into_words(q: str):
    # Remove all syntax symbols
    syntax_marks = ",.!?-"
    for sym in syntax_marks:
        q = q.replace(sym, ' ')

    # Split into words
    words = q.lower().strip().split()
    words = [w.strip() for w in words]
    words = [w for w in words if w]

    return words


def word_in_words(word: str, words: List[str]):
    for w in words:
        if w.startswith(word):
            return True
    return False


def search_stickers(query: str):
    query_words = into_words(query)

    stickers = []
    for file_id, texts in config.STICKERS.items():
        texts_string = " ".join(texts).lower()
        texts_words = into_words(texts_string)
        if all([ word_in_words(w, texts_words) for w in query_words ]):
            stickers.append(file_id)

    return stickers


def on_query(bot: Bot, update: Update):
    inline_query = update.inline_query

    if not inline_query:
        return

    print("Inline query from {}:{} with text '{}'".format(
        inline_query.from_user.id, inline_query.from_user.first_name,
        inline_query.query))

    stickers = search_stickers(inline_query.query)

    # No more than 50 results are allowed by telegram bot api.
    if len(stickers) > 50:
        stickers = stickers[:50]

    results = [InlineQueryResultCachedSticker(fid, fid) for fid in stickers]
    bot.answer_inline_query(inline_query.id, results, cache_time=600)


def on_message(bot: Bot, update: Update):
    message = update.message

    if not message:
        return

    is_sticker = bool(message.sticker)
    sticker_is_in_db = is_sticker and message.sticker.file_id in config.STICKERS

    if sticker_is_in_db:
        print("Message from {}:{} with known sticker '{}'".format(
            message.from_user.id, message.from_user.first_name,
            message.sticker.file_id))
        bot.send_message(
            message.chat.id,
            config.HYPE_MSG,
            parse_mode='Markdown')
    elif is_sticker:
        print("Message from {}:{} with unknown sticker '{}'".format(
            message.from_user.id, message.from_user.first_name,
            message.sticker.file_id))
        bot.send_message(
            message.chat.id,
            config.STICKER_DATA_MSG.format(file_id=message.sticker.file_id),
            parse_mode='Markdown')
    else:
        print("Message from {}:{} with text '{}'".format(
            message.from_user.id, message.from_user.first_name, message.text))
        bot.send_message(
            message.chat.id,
            config.INSTRUCTIONS_MSG.format(stickers_count=len(config.STICKERS)),
            parse_mode='Markdown')


def main():
    if not config.TELEGRAM_BOT_KEY:
        raise RuntimeError("Please, put you bot api key into the config.")

    print("Stickers in the DB: {}".format(len(config.STICKERS)))

    updater = Updater(token=config.TELEGRAM_BOT_KEY)
    dispatcher = updater.dispatcher

    query_handler = InlineQueryHandler(on_query)
    dispatcher.add_handler(query_handler)

    msg_handler = MessageHandler(Filters.all, on_message)
    dispatcher.add_handler(msg_handler)

    print("Starting the druzhbot...")
    updater.start_polling()


if __name__ == '__main__':
    main()
