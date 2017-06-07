#!/usr/bin/env python3
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters

import config


def on_message(bot: Bot, update: Update):
    if not update.message:
        return

    bot.send_message(update.message.chat.id, "Hello world!")


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
