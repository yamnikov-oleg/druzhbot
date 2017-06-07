#!/usr/bin/env python3
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters

import config


def on_message(bot: Bot, update: Update):
    message = update.message

    if not message:
        return

    if message.sticker:
        bot.send_message(
            message.chat.id,
            config.STICKER_DATA_MSG.format(file_id=message.sticker.file_id),
            parse_mode='Markdown')
    else:
        bot.send_message(
            message.chat.id,
            config.INSTRUCTIONS_MSG,
            parse_mode='Markdown')


def main():
    if not config.TELEGRAM_BOT_KEY:
        raise RuntimeError("Please, put you bot api key into the config.")

    updater = Updater(token=config.TELEGRAM_BOT_KEY)
    dispatcher = updater.dispatcher

    msg_handler = MessageHandler(Filters.all, on_message)
    dispatcher.add_handler(msg_handler)

    print("Starting the druzhbot...")
    updater.start_polling()


if __name__ == '__main__':
    main()
