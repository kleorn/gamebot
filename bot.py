#pip install pyTelegramBotAPI
#@reboot cd /home/admin/web/m-kan.ru/private/gamebot && python3 bot.py
import random
import os
if os.path.exists('config_secret.py'):
	import config_secret as config
else:
	import config
import telebot

class GameServer:
	def __init__(self):
		self.selected_games = {} #словарь user_id: объект игры
		self.games = [
			{'func': KupiSlonaGame, 'num': '1', 'name': 'Купи слона'},
			{'func': MulTableGame, 'num': '2', 'name': 'Таблица умножения'},
			{'func': SuperMulTableGame, 'num': '3', 'name': 'Супертаблица умножения'}
		]
		self.data = {}

	def list_games(self, message):
		self.selected_games[message.chat.id] = SelectGame
		games_list_str = 'Выбери игру:\n'
		for g in self.games:
			games_list_str += g['num'] + ' - ' + g['name'] + '\n'
		return games_list_str


class Game:
	def __init__(self):
		self.data = {}

class SelectGame(Game):
	def reply(message):
		if message.text in [game['num'] for game in srv.games]:
			game = [game for game in srv.games if game['num'] == message.text][0]
			srv.selected_games[message.chat.id] = game['func']
			return 'Приготовься! Начинаем игру \"' + game['name'] + '\"\nДля возврата к выбору игры отправь \"!\"\n\n' + game['func'].start(message)

class EnterUrName(Game): #статический класс
	@classmethod
	def reply(cls, message):
		uid = message.chat.id
		srv.data[uid] = {}
		srv.data[uid]['username'] = message.text
		return 'А я - робот! Приятно познакомиться, ' + message.text + '!'
	@classmethod
	def start(cls, message):
		uid = message.chat.id
		return 'Как тебя зовут?'


class KupiSlonaGame(Game): #статический класс
	data = {}
	@classmethod
	def reply(cls, message):
		return 'Все говорят \"' + message.text + '\", а ты купи слона'
	@classmethod
	def start(cls, message):
		uid = message.chat.id
		cls.data[uid] = {}
		return 'УНИКАЛЬНОЕ ПРЕДЛОЖЕНИЕ!!! Купи слона!'

class MulTableGame(Game):
	data = {}
	@classmethod
	def start(cls, message):
		uid = message.chat.id
		cls.data[uid] = {}
		cls.data[uid]['score'] = 0
		return cls.ask_question(message)

	@classmethod
	def reply(cls, message):
		uid = message.chat.id
		if 'question' in cls.data[uid]: #если уже задан вопрос
			if message.text == cls.data[uid]['answer']:
				cls.data[uid].pop('question')
				cls.data[uid]['score'] += int(cls.data[uid]['answer'])
				return 'Правильно, Анютка, ' + message.text + '! \n Счет - ' + str(cls.data[uid]['score']) + ' очков\nДавай ещё!\n' + cls.ask_question(message)
			else:
				return "Давай ещё варианты!"
		else:
			return cls.ask_question(cls, message)

	@classmethod
	def ask_question(cls, message):
		uid = message.chat.id
		a = random.randint(1, 10)
		b = random.randint(1, 10)
		cls.data[uid]['question'] = str(a) + ' x ' + str(b) + '?'
		cls.data[uid]['answer'] = str(a * b)

		return cls.data[uid]['question']

class SuperMulTableGame(Game):
	data = {}
	@classmethod
	def start(cls, message):
		uid = message.chat.id
		cls.data[uid] = {}
		cls.data[uid]['score'] = 0
		return cls.ask_question(message)

	@classmethod
	def reply(cls, message):
		uid = message.chat.id
		if 'question' in cls.data[uid]: #если уже задан вопрос
			if message.text == cls.data[uid]['answer']:
				cls.data[uid].pop('question')
				cls.data[uid]['score'] += int(cls.data[uid]['answer'])*100
				return 'Правильно, Анютка, ' + message.text + '! \n Счет - ' + str(cls.data[uid]['score']) + ' очков\nДавай ещё!\n' + cls.ask_question(message)
			else:
				return "Давай ещё варианты!"
		else:
			return cls.ask_question(cls, message)

	@classmethod
	def ask_question(cls, message):
		uid = message.chat.id
		a = random.randint(10, 15)
		b = random.randint(1, 15)
		cls.data[uid]['question'] = str(a) + ' x ' + str(b) + '?'
		cls.data[uid]['answer'] = str(a * b)
		return cls.data[uid]['question']



srv = GameServer()
bot = telebot.TeleBot(config.TOKEN)

#задаем реакцию на получение ботом текстового сообщения
@bot.message_handler(content_types=['text'])
def repeat_all_messages(message):
	if message.chat.id not in srv.selected_games or message.text == '!':
		reply_func = srv.list_games
	# elif selected_games[message.chat.id] == 'select_game' MODE == 'select_game'
	else:
		reply_func = srv.selected_games[message.chat.id].reply
	reply = reply_func(message)

	bot.send_message(message.chat.id, reply)
	# bot.send_message(message.chat.id, message.chat.id)

bot.polling(non_stop=True) #запускаем постоянную обработку сообщений