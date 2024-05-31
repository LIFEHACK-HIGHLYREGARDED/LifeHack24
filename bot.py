from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler

import validators

TOKEN: Final = '7441258704:AAGD_VLp387mOUExezmhOgbIBuuWyyPX0X0'
USERNAME: Final = '@TerrorInsightBot'


# Commands
def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return update.message.reply_text('Hello, I am TerrorInsight, your one stop shop for terrorism information! What would you like me to do today?\n\nType "/help" for the list of commands.')

def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return update.message.reply_text('Here is the list of commands:\n\n/add_link - submit links to articles for me to process\n/add_file - submit links to articles for me to process\n/query - ask a question, and I will reply you based on information you have given me')

def file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        new_file = update.message.document.get_file()
        return update.message.reply_text('Thanks for the report! Looking forward to reading it!')
    else:
        return update.message.reply_text('File not detected! To add report files, type "/add_file", then attach the report.')

def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wordArr = update.message.text.split(' ')
    if not len(wordArr) > 1:
        return update.message.reply_text(
            'To add article links, type "/add_link" followed by a space, and then the links.\n\nExample: /add_link https://google.com https://yahoo.com')
    
    wordArr.remove(wordArr[0])
    validLinks = []
    reply = ''
    for link in wordArr:
        if validators.url(link):
            validLinks.append(link)
        else:
            reply += link + ' is invalid. Try another one!\n'
    
    if len(validLinks) > 0:
        reply += 'Thanks for the links! Looking forward to reading the articles!'
    
    # LLM goes to link and reads articles

    return update.message.reply_text(f'{reply}')

def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arr = update.message.text.split(' ', 1)
    if not len(arr) > 1:
        return update.message.reply_text(
            'To pose queries, type "/query" followed by a space, and then the question.\n\nExample: /query How many terrorism incidents were there in 2010?')
    
    question = arr[1]
    # send question to LLM
    # get answer from LLM

    return update.message.reply_text('answer goes here')


# Messages
def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text # incoming message

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    return update.message.reply_text('Sorry, I cannot understand that. Type "/help" for the list of commands!')


# Errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('starting bot...')
    app = Application.builder().token(TOKEN).build()

    # commands
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('add_link', link))
    app.add_handler(CommandHandler('add_file', file))
    app.add_handler(CommandHandler('query', query))

    # messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL & filters.Caption('/add_file'), file))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.Document.ALL), handle_message))

    # errors
    app.add_error_handler(error)

    # polls the bot
    print('polling...')
    app.run_polling(poll_interval=1)