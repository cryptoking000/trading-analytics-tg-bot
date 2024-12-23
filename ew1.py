from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes
 
async def callback_alarm(context: ContextTypes.DEFAULT_TYPE):
    # Beep the person who called this alarm:
    await context.bot.send_message(chat_id=context.job.chat_id, text=f'BEEP {context.job.data}!')
 

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("👉hello command----")
        message1 = (
            "👋 *Hello\\!*\n\n"
            "I'm here to assist you with all your crypto\\-related queries\\. Whether you're looking for market insights, news, or just want to chat, I'm here to help\\!\n\n"
            "To get started, simply type /start or use the buttons below\\.\n\n"
            "🌟 *Enjoy your crypto journey*"
        )
        await update.message.reply_text(text=message1)
        

    except Exception as e:
        
        await update.message.reply_text("An error occurred. Please try again later.")
 
async def callback_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    name = update.effective_chat.full_name
    await context.bot.send_message(chat_id=chat_id, text='Setting a timer for 1 minute!')
    # Set the alarm:
    context.job_queue.run_once(callback_alarm, 60, data=name, chat_id=chat_id)
 
application = Application.builder().token('7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4').build()
timer_handler = CommandHandler('timer', callback_timer)
application.add_handler(CommandHandler("hello", hello))
application.add_handler(timer_handler)
application.run_polling()