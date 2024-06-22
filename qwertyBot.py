import telebot
import time
from telebot import types
import io
from keras.preprocessing import image 
from keras.models import load_model 
from keras.applications.vgg16 import preprocess_input 
import numpy as np 
import requests

bot = telebot.TeleBot('7289867286:AAHWCSf58-R9BFrO3UoXcoNZPoeIuCWuJqU')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')    
    time.sleep(1.25)
    bot.send_message(message.chat.id, 'Я бот, который поможет вам найти пневмонию в ваших легких. 🤖')
    time.sleep(2)
    bot.send_message(message.chat.id, 'Пришлите пожалуйста рентгеновский снимок вашей грудной клетки. 🩻')
    
response = requests.get('https://github.com/GOGSIM/Pneumonia-Finder/blob/7a1f41f2a52a5825ce54a1c66c10947d55eaa3e4/model_ASV.h5', stream=True) 
model = io.BytesIO()
for chunk in response.iter_content(chunk_size=8192):
    if chunk:
        model.write(chunk)
model.seek(0)          

@bot.message_handler(content_types=['photo'])
def photo(message):
    photografia = message.photo[-1]
    file_info = bot.get_file(photografia.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    byte_stream = io.BytesIO(downloaded_file)
    img = image.load_img(byte_stream, target_size=(224,224))
    imagee = image.img_to_array(img)  
    imagee = np.expand_dims(imagee, axis=0) 
    img_data = preprocess_input(imagee) 
    prediction = model.predict(img_data)
    if prediction[0][0] > prediction[0][1]:
        bot.reply_to(message, 'Пневмония <b>не обнаружена</b>, y вас все хорошо :)', parse_mode='html') 
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Больницы рядом', url='https://yandex.ru/maps/1/moscow-and-moscow-oblast/category/hospital/')
        btn2 = types.InlineKeyboardButton('Подобрать врача', url='https://doctown.ru/kto-lechit/pnevmoniyu/')
        btn3 = types.InlineKeyboardButton('Записаться на флюорографию', url='https://docdoc.ru/service/diagnostica/fluorografiya/')
        btn4 = types.InlineKeyboardButton('Симптомы пневмонии', url='https://probolezny.ru/pnevmoniya/')
        markup.row(btn1, btn2)
        markup.row(btn3, btn4)
        bot.reply_to(message, 'У вас <b>обнаружена</b> пневмония, вам следует обратиться к врачу!', reply_markup=markup, parse_mode='html')
    byte_stream.close()

@bot.message_handler(commands=['hospitals'])
def hospitals(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Ссылка', url='https://yandex.ru/maps/1/moscow-and-moscow-oblast/category/hospital/', parse_mode='html'))
        bot.send_message(message.chat.id, 'Больницы рядом 🏥😷', reply_markup=markup)
        
@bot.message_handler(commands=['symptoms'])
def hospitals(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Ссылка', url='https://probolezny.ru/pnevmoniya/', parse_mode='html'))
        bot.send_message(message.chat.id, 'Симптомы пневмонии 😵‍💫', reply_markup=markup)

@bot.message_handler(commands=['help'])
def doctor(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Ссылка', url='https://doctown.ru/kto-lechit/pnevmoniyu/', parse_mode='html'))
        bot.send_message(message.chat.id, 'Подобрать врача 👨🏻‍⚕️ —  <u>+74951528567</u>', reply_markup=markup, parse_mode='html')

@bot.message_handler(commands=['takephoto'])
def takephoto(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Ссылка', url='https://docdoc.ru/service/diagnostica/fluorografiya/', parse_mode='html'))
        bot.send_message(message.chat.id, 'Записаться на флюорографию 🩻', reply_markup=markup)

bot.polling(non_stop=True)
