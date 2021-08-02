# -*- coding: utf-8 -*-
import sqlite3
from telebot import *
import telebot
import random
import threading
import requests
import json

lock = threading.Lock()

# database connect
global db, sql
db = sqlite3.connect('newbot.db', check_same_thread=False)
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS files (
    usid BIGINT,
    pass TEXT,
    channel BIGINT,
    info TEXT,
    fake TEXT,
    type TEXT
)""")
db.commit()

# telegram api connect
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

token = config["token"]
bot = telebot.TeleBot(token)

# handlers
# start message
@bot.message_handler(commands=["start"])
def start(message):
  info = telebot.util.extract_arguments(message.text)
  sql.execute(f"SELECT pass FROM files WHERE pass = '{info}'")
  if sql.fetchone() is None:
    bot.send_message(message.chat.id, "👋 <b>Привет!</b>\n\n<i>Я могу скрыть текст сообщения от тех, кто не подписан на твой канал.</i>\n\n<b>Тебе всего лишь нужно:</b>\n\n1. Добавить меня в свой канал и выдать админа с правами - 'Изменять информацию о канале' и 'Добавлять участников'\n2. Получить ID своего канала. Это можно сделать переслав боту @myidbot сообщение из своего канала\n3. Прописать комманду /new и следовать инструкциям\nТак же я поддерживаю <b>Аудио Файлы и Голосовые сообщения!</b>\nЧтобы загрузить аудио файл в этого бота, просто отправь мне этот аудио файл или голосовое сообщение и следуй инструкциям!(комманду /new не писать)\n\nРазработчик: @kirillsaint_info, https://kirillsaint.xyz\nСвязь с разработчиком: @saintfukk2, @kirillsaint_bot\nБлог разработчика: @kirillsaint", parse_mode="HTML")
  else:
  	try:
	  	for ci in sql.execute(f"SELECT channel FROM files WHERE pass = '{info}'"):
	  		CHAT_ID = ci[0]
	  	USER_ID = message.chat.id
	  	response = requests.get(f'https://api.telegram.org/bot{token}/getChatMember?chat_id={CHAT_ID}&user_id={USER_ID}')
	  	status = json.loads(response.text)["result"]["status"]
	  	if status == 'left':
	  		sub = False
	  	else:
	  		sub = True
  	except:
  		sub = False

  	try:
  		if sub == True:
  			for t in sql.execute(f"SELECT type FROM files WHERE pass = '{info}'"):
  				typ = t[0]
  			print(typ)
  			if typ == 'text':
  				for i in sql.execute(f"SELECT info FROM files WHERE pass = '{info}'"):
  					info = i[0]
  				bot.send_message(message.chat.id, info)
  			elif typ == 'audio':
  				bot.send_audio(message.chat.id, open(f"{info}-audio.mp3", "rb"))
  			elif typ == 'voice':
  				bot.send_voice(message.chat.id, open(f"{info}-voice.ogg", "rb"))
  		else:
  			for f in sql.execute(f"SELECT fake FROM files WHERE pass = '{info}'"):
  				fake = f[0]
  			bot.send_message(message.chat.id, fake)
  	except:
  		try:
  			for f in sql.execute(f"SELECT fake FROM files WHERE pass = '{info}'"):
  				fake = f[0]
  			bot.send_message(message.chat.id, fake)
  		except:
  			bot.send_message(message.chat.id, "Произошла какая-то ошибка!")

# new message
@bot.message_handler(commands=["new"])
def new1(message):
    bot.send_message(message.chat.id, "*Введите ID канала:* ", parse_mode="Markdown")
    bot.register_next_step_handler(message, new2)

# functions
def new2(message):
    try:
        global ch
        ch = int(message.text)
        bot.send_message(message.chat.id, "*Введите текст секретного сообщения:* ", parse_mode="Markdown")
        bot.register_next_step_handler(message, new3)
    except:
        bot.send_message(message.chat.id, "Это не айди канала! ", parse_mode="Markdown")
 
def new3(message):
    global info
    info = message.text
    bot.send_message(message.chat.id, "*Введите текст сообщения, которое будет отправляться в случае если пользователь не подписан на канал:* ", parse_mode="Markdown")
    bot.register_next_step_handler(message, new4)

def new4(message):
	global fake
	fake = message.text
	try:
	  chars = 'abcdefghyjklmnopqrstuvwxyz'
	  chars += chars.upper()
	  nums = str(1234567890)
	  chars += nums
	  length = 8
	  pas = "".join(random.sample(chars, length))
	  finfo = [message.chat.id, pas, ch, info, fake, 'text']
	  sql.execute(f"INSERT INTO files VALUES (?, ?, ?, ?, ?, ?)", finfo)
	  db.commit()
	  bot.send_message(message.chat.id, f"*Твой текст доступен по ссылке:* https://t.me/channeltextbot?start={pas}", parse_mode="Markdown")
	except:
	  bot.send_message(message.chat.id, f"Ошибка!")

@bot.message_handler(content_types=["audio"])
def audio(message):
	try:
		chars = 'abcdefghyjklmnopqrstuvwxyz'
		chars += chars.upper()
		nums = str(1234567890)
		chars += nums
		length = 9
		global pas
		global f
		global fa
		pas = "".join(random.sample(chars, length))
		file_info = bot.get_file(message.audio.file_id)
		file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
		with open(f'{pas}-audio.mp3','wb') as f:
			f.write(file.content)
		fa = f'{pas}-audio.mp3'
		bot.send_message(message.chat.id, "*Введите текст сообщения, которое будет отправляться в случае если пользователь не подписан на канал:* ", parse_mode="Markdown")
		bot.register_next_step_handler(message, newfile1)
	except:
		bot.send_message(message.chat.id, 'Ошибка!')

def newfile1(message):
	try:
		global fake
		fake = message.text
		bot.send_message(message.chat.id, "*Введите ID канала:* ", parse_mode="Markdown")
		bot.register_next_step_handler(message, newfile)
	except:
		bot.send_message(message.chat.id, 'Ошибка!')

def newfile(message):
	try:
		ch = message.text
		finfo = [message.chat.id, pas, ch, fa, fake, 'audio']
		sql.execute(f"INSERT INTO files VALUES (?, ?, ?, ?, ?, ?)", finfo)
		db.commit()
		bot.send_message(message.chat.id, f"*Твой файл доступен по ссылке:* https://t.me/channeltextbot?start={pas}", parse_mode="Markdown")
	except:
		bot.send_message(message.chat.id, 'Ошибка!')

@bot.message_handler(content_types=["voice"])
def voice(message):
	try:
		chars = 'abcdefghyjklmnopqrstuvwxyz'
		chars += chars.upper()
		nums = str(1234567890)
		chars += nums
		length = 9
		global pas
		global f
		global fa
		pas = "".join(random.sample(chars, length))
		file_info = bot.get_file(message.voice.file_id)
		file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
		with open(f'{pas}-voice.ogg','wb') as f:
			f.write(file.content)
		fa = f'{pas}-voice.mp3'
		bot.send_message(message.chat.id, "*Введите текст сообщения, которое будет отправляться в случае если пользователь не подписан на канал:* ", parse_mode="Markdown")
		bot.register_next_step_handler(message, newvoice1)
	except:
		bot.send_message(message.chat.id, 'Ошибка!')

def newvoice1(message):
	try:
		global fake
		fake = message.text
		bot.send_message(message.chat.id, "*Введите ID канала:* ", parse_mode="Markdown")
		bot.register_next_step_handler(message, newvoice)
	except:
		bot.send_message(message.chat.id, 'Ошибка!')

def newvoice(message):
	try:
		ch = message.text
		finfo = [message.chat.id, pas, ch, fa, fake, 'voice']
		sql.execute(f"INSERT INTO files VALUES (?, ?, ?, ?, ?, ?)", finfo)
		db.commit()
		bot.send_message(message.chat.id, f"*Твое голосовое сообщение доступен по ссылке:* https://t.me/channeltextbot?start={pas}", parse_mode="Markdown")
	except:
		bot.send_message(message.chat.id, 'Ошибка!')


# polling
bot.polling(none_stop=True)

# by @kirillsaint / https://github.com/kirillsaint/
