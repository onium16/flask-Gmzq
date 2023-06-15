import os
import time
from dotenv import load_dotenv   # Local mode ------------------------------------------
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from main_reposter import start_repost_links


def start_repost_bot():
    # Load environment variables 
    load_dotenv()  # Local mode  ------------------------------------------

    # Get bot token from environment variables
    BOT_TOKEN = os.getenv("BOT_TOKEN")   # Local mode ------------------------------------------
    # BOT_TOKEN = os.environ.get('TOKEN')  # Server mode ------------------------------------------

    # Create bot instance
    bot = Bot(token=BOT_TOKEN)

    url = 'https://finance.yahoo.com/'
    hashes_file_path = 'hashes.txt'
    interval = 10  # Default interval, in case user input is invalid
    set_interval_flag = False

    def start(update: Update, context: CallbackContext) -> None:
        """Handler for the /start command"""
        chat_id = update.effective_chat.id
        update.message.reply_text('Hello! Send the command /news to receive news.')

    def news(update: Update, context: CallbackContext) -> None:
        """Handler for the /news command"""
        chat_id = update.effective_chat.id
        update.message.reply_text('Please set the interval for checking new articles (in minutes):')
        global set_interval_flag
        set_interval_flag = True

    def set_interval(update: Update, context: CallbackContext) -> None:
        """Handler for setting the interval"""
        chat_id = update.effective_chat.id
        user_input = update.message.text

        try:
            global interval
            interval = int(user_input)
            context.job_queue.run_repeating(send_news, interval=interval*60, context=(chat_id, bot))

            update.message.reply_text(f'News sending cycle started with an interval of {interval} minutes. Use the /stop command to stop.')
        except ValueError:
            update.message.reply_text('Invalid input. Please enter a valid interval in minutes.')

    def send_news(context: CallbackContext) -> None:
        """Function for sending news"""
        chat_id, bot = context.job.context

        news_data = start_repost_links(hashes_file_path, url)  # Connect the script for finding new links
        if len(news_data) > 0 and news_data != 'New links not found':
            for link in news_data:
                if link:
                    bot.send_message(chat_id=chat_id, text=link)
        else:
            bot.send_message(chat_id=chat_id, text=news_data)

    def stop(update: Update, context: CallbackContext) -> None:
        """Handler for the /stop command"""
        chat_id = update.effective_chat.id
        context.job_queue.stop()

        update.message.reply_text('News sending cycle stopped.')

    def main() -> None:
        updater = Updater(token=BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("news", news))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, set_interval))
        dispatcher.add_handler(CommandHandler("stop", stop))

        updater.start_polling()
       
        while True:
            try:
                time.sleep(2)  # Пауза в секундах между проверками состояния бота

                # Дополнительные проверки и обновления состояния бота, если необходимо

            except KeyboardInterrupt:
                updater.stop()
                break

            except Exception as e:
                print(f"An error occurred: {str(e)}")

    main()



if __name__ == '__main__':
    start_repost_bot()
