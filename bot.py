from config import TOKEN
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
import handlers


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # command hanlers
    dispatcher.add_handler(CommandHandler('start', handlers.start))

    # message handler
    dispatcher.add_handler(MessageHandler(Filters.location, handlers.send_weather_by_location))
    dispatcher.add_handler(MessageHandler(Filters.text("📞 Aloqa"), handlers.send_contact))
    dispatcher.add_handler(MessageHandler(Filters.text("⛅️ Hozirgi ob-havo"), handlers.send_current_weather))
    dispatcher.add_handler(MessageHandler(Filters.text("🕔 Soatlik ob-havo"), handlers.send_hourly_weather))
    dispatcher.add_handler(MessageHandler(Filters.text("🗓 Haftalik ob-havo"), handlers.send_weekly_weather))
    dispatcher.add_handler(MessageHandler(Filters.text("📍 Hududni o'zgartirish"), handlers.change_location))
    dispatcher.add_handler(MessageHandler(Filters.text("Orqaga"), handlers.go_back))
    dispatcher.add_handler(MessageHandler(Filters.text, handlers.handle_text))

    # start bot
    updater.start_polling()
    updater.idle()

main()
