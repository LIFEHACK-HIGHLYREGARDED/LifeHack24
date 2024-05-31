from backend import take_input
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler
from typing import Final

import docx
import fitz
import pytesseract
import validators

TOKEN: Final = '7441258704:AAGD_VLp387mOUExezmhOgbIBuuWyyPX0X0'
USERNAME: Final = '@TerrorInsightBot'


# Commands
def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return update.message.reply_text('Hello, I am TerrorInsight, your one stop shop for terrorism information! What would you like me to do today?\n\nType "/help" for the list of commands.')

def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return update.message.reply_text('Here is the list of commands:\n\n/add_link - submit links to articles for me to process\n/add_file - submit articles and reports for me to process\n/query - ask a question, and I will reply you based on information you have given me')
        
def file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        # Download the file
        file_path = f"./{update.message.document.file_name}"
        update.message.document.get_file().download(file_path)

        # Extract text
        text_content = ""
        if file_path.endswith('.pdf'):
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            doc.close()
        elif file_path.endswith('.jpeg') or file_path.endswith('.jpg'):
            image = Image.open(file_path)
            text_content = pytesseract.image_to_string(image)
        elif file_path.endswith('.docx'):
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
        else:
            return update.message.reply_text('This file type is not supported. I can only take in DOCX, JPEG and PDF files!')
        
        # HERE, MODEL ACCEPTS AND PROCESSES TEXT
        take_input(text_content)

        return update.message.reply_text('Thanks for the report! Looking forward to reading it!')
    else: # No documents
        return update.message.reply_text('File not detected! Attach some documents for me to process! (No need to repeat the "/add_file" keyword!)')
    
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
    
    # HERE, MODEL ACCEPTS AND PROCESSES TEXT
    for link in validLinks:
        take_input(link)

    return update.message.reply_text(f'{reply}')

def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arr = update.message.text.split(' ', 1)
    if not len(arr) > 1:
        return update.message.reply_text(
            'To pose queries, type "/query" followed by a space, and then the question.\n\nExample: /query How many terrorism incidents were there in 2010?')
    
    question = arr[1]
    # here, send question to LLM
    # then, get answer from LLM

    return update.message.reply_text(f'Question: {question}\n\nAnswer: [insert answer here]')


# Messages
def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text # incoming message
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    return update.message.reply_text('Sorry, I do not understand that. Type "/help" for the list of commands!')

def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    file = update.message.document.get_file()

    # here, LLM accepts and processes file

    print(f'User ({update.message.chat.id}) in {message_type} sent a document: {file}')

    return update.message.reply_text('Thanks for the report! Looking forward to reading them!')


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
    app.add_handler(MessageHandler(filters.Document.ALL & ~filters.TEXT, handle_document))

    # errors
    app.add_error_handler(error)

    # polls the bot
    print('polling...')
    app.run_polling(poll_interval=1)