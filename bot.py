#pip install pyTelegramBotAPI
#@reboot cd /home/admin/web/m-kan.ru/private/gamebot && python3 bot.py
try:
	#import sys
	import logging
	from logging.handlers import RotatingFileHandler  # просто import logging недостаточно!
	import random
	import os
	if os.path.exists('config_secret.py'):
		import config_secret
		CONFIG_SECRET_IMPORTED = True
	else:
		CONFIG_SECRET_IMPORTED = False
	import config
	import telebot
	import csv
	LOG_FILENAME='gamebot.csv'

	class GameServer:
		def __init__(self):
			self.selected_games = {} #словарь user_id: объект игры
			self.games = [
				{'func': KupiSlonaGame, 'num': '1', 'name': 'Купи слона'},
				{'func': MulTableGame, 'num': '2', 'name': 'Таблица умножения'},
				{'func': SuperMulTableGame, 'num': '3', 'name': 'Супертаблица умножения'},
				{'func': EngDictGame, 'num': '4', 'name': 'English words'}
			]
			self.data = {}

		def list_games(self, message):
			self.selected_games[message.uid] = SelectGame
			games_list_str = 'Выбери игру:\n'
			for g in self.games:
				games_list_str += g['num'] + ' - ' + g['name'] + '\n'
			return games_list_str

		def get_config(self, var_name):
			if CONFIG_SECRET_IMPORTED:
				return getattr(config_secret, var_name, getattr(config, var_name))
			else:
				return getattr(config, var_name, '')

	class Game:
		def __init__(self):
			self.data = {}

	class SelectGame(Game):
		def reply(message):
			if message.text in [game['num'] for game in srv.games]:
				game = [game for game in srv.games if game['num'] == message.text][0]
				srv.selected_games[message.uid] = game['func']
				return 'Приготовься! Начинаем игру \"' + game['name'] + '\"\nДля возврата к выбору игры отправь \"!\"\n\n' + game['func'].start(message)

	class EnterUrName(Game): #статический класс
		@classmethod
		def reply(cls, message):
			srv.data[message.uid] = {}
			srv.data[message.uid]['username'] = message.text
			return 'Приятно познакомиться, ' + message.text + '! А я - ' + srv.get_config('BOT_NAME') + '!\nЧтобы представиться заново, введи "?"\n' + srv.list_games(message)
		@classmethod
		def start(cls, message):
			return 'Как тебя зовут (я записываю рейтинг)?' #Анютка?😀🐁


	class KupiSlonaGame(Game): #статический класс
		data = {}
		@classmethod
		def reply(cls, message):
			return 'Все говорят \"' + message.text + '\", а ты купи слона'
		@classmethod
		def start(cls, message):
			cls.data[message.uid] = {}
			return 'УНИКАЛЬНОЕ ПРЕДЛОЖЕНИЕ!!! Купи слона!'

	class MulTableGame(Game):
		data = {}
		@classmethod
		def start(cls, message):
			cls.data[message.uid] = {}
			cls.data[message.uid]['score'] = 0
			return cls.ask_question(message)

		@classmethod
		def reply(cls, message):
			if 'question' in cls.data[message.uid]: #если уже задан вопрос
				if message.text == cls.data[message.uid]['answer']:
					cls.data[message.uid].pop('question')
					cls.data[message.uid]['score'] += int(cls.data[message.uid]['answer'])
					return 'Правильно, ' + srv.data[message.uid]['username'] + ', ' + message.text + '! \nСчет - ' + str(cls.data[message.uid]['score']) + ' очков\nДавай ещё!\n' + cls.ask_question(message)
				else:
					return "Давай ещё варианты!"
			else:
				return cls.ask_question(cls, message)

		@classmethod
		def ask_question(cls, message):
			a = random.randint(1, 10)
			b = random.randint(1, 10)
			cls.data[message.uid]['question'] = str(a) + ' x ' + str(b) + '?'
			cls.data[message.uid]['answer'] = str(a * b)

			return cls.data[message.uid]['question']

	class SuperMulTableGame(Game):
		data = {}
		@classmethod
		def start(cls, message):
			cls.data[message.uid] = {}
			cls.data[message.uid]['score'] = 0
			return cls.ask_question(message)

		@classmethod
		def reply(cls, message):
			if 'question' in cls.data[message.uid]: #если уже задан вопрос
				if message.text == cls.data[message.uid]['answer']:
					cls.data[message.uid].pop('question')
					cls.data[message.uid]['score'] += int(cls.data[message.uid]['answer'])*100
					return 'Правильно, ' + srv.data[message.uid]['username'] + ', ' + message.text + '! \nСчет - ' + str(cls.data[message.uid]['score']) + ' очков\nДавай ещё!\n' + cls.ask_question(message)
				else:
					return "Давай ещё варианты!"
			else:
				return cls.ask_question(cls, message)

		@classmethod
		def ask_question(cls, message):
			a = random.randint(10, 15)
			b = random.randint(1, 15)
			cls.data[message.uid]['question'] = str(a) + ' x ' + str(b) + '?'
			cls.data[message.uid]['answer'] = str(a * b)
			return cls.data[message.uid]['question']

	class EngDictGame(Game):
		data = {}
		common_eng_dict = {}
		filename = 'engdict.csv'
		with open(filename, encoding='utf-8') as f:
			reader = csv.reader(f, delimiter=';')
			for row in reader:
				common_eng_dict[row[1]] = row[0] #файл: слово;перевод. словарь: { перевод: слово }

		@classmethod
		def start(cls, message):
			cls.data[message.uid] = {}
			cls.data[message.uid]['score'] = 0
			cls.data[message.uid]['eng_dict']=cls.common_eng_dict.copy()
			return cls.ask_question(message)

		@classmethod
		def reply(cls, message):
			if 'question' in cls.data[message.uid]: #если уже задан вопрос
				if message.text.lower().strip() == cls.data[message.uid]['answer']:
					cls.data[message.uid]['eng_dict'].pop(cls.data[message.uid]['question_word'])
					if srv.get_config('DONT_REPEAT_WORDS'):
						cls.data[message.uid].pop('question')
						cls.data[message.uid].pop('question_word')
					cls.data[message.uid]['score'] += 20

					reply_text = 'Правильно, ' + srv.data[message.uid]['username'] + ', ' + message.text + '! \nСчет - ' + str(cls.data[message.uid]['score']) + ' очков\nДавай ещё!\n'

					if len(cls.data[message.uid]['eng_dict'])==0:
						cls.data[message.uid]['eng_dict'] = cls.common_eng_dict.copy()
						reply_text += 'ПОЗДРАВЯЮ! ВСЕ СЛОВА СНОВА ПОБЕЖДЕНЫ!\n'

					return reply_text + cls.ask_question(message)
				else:
					return "Давай ещё варианты!\nПодсказка: " + cls.data[message.uid]['answer'][::-1]
			else:
				return cls.ask_question(cls, message)

		@classmethod
		def ask_question(cls, message):
			a = random.randint(0, len(cls.data[message.uid]['eng_dict']) - 1)
			dict_keys=list(cls.data[message.uid]['eng_dict'].keys())
			question_icons=['🇬🇧','🚢','🏰','🎡']
			question_icon = question_icons[random.randint(0, len(question_icons)-1)]
			cls.data[message.uid]['question'] = 'What\'s English for \'' + dict_keys[a] + '\'? ' + question_icon

			cls.data[message.uid]['question_word'] = dict_keys[a]
			cls.data[message.uid]['answer'] = cls.data[message.uid]['eng_dict'][dict_keys[a]]

			return cls.data[message.uid]['question']

	srv = GameServer()
	#print(sys.modules)
	if not os.path.exists('logs'):
		os.mkdir('logs')
	if not os.path.exists('logs/' + LOG_FILENAME):
		with open('logs/' + LOG_FILENAME, 'w', newline='', encoding='utf-8') as logfile:
			# conf_file.write(str(codecs.BOM_UTF8)) - не работает
			bom_utf8 = u'\ufeff'
			header = 'Timestamp;Level;Module;Line;UID;TG Username;Username;Chat name;Game;User message;Reply\n'
			logfile.write(bom_utf8 + header)  # начинаем файл с UTF-8 Byte Order Mask (BOM)

	file_handler = logging.handlers.RotatingFileHandler(filename='logs/'+LOG_FILENAME, encoding='utf-8', mode='a',
	                                                    maxBytes=1000000, backupCount=10, delay=False)
	handlers_list = [file_handler]
	logging.basicConfig(handlers=handlers_list,
	                    format='%(asctime)s;%(levelname)s;%(name)s;%(lineno)s;%(message)s', level=srv.get_config('LOG_LEVEL'),
	                    datefmt='%m-%d-%Y %H:%M:%S')  # вызывать 1 раз

	bot = telebot.TeleBot(srv.get_config('TOKEN'))


	#задаем реакцию на получение ботом текстового сообщения
	@bot.message_handler(content_types=['text'])
	def repeat_all_messages(message):
		try:
			#print(message)
			if srv.get_config('COOPERATIVE_PLAY_IN_GROUP'):
				message.uid = message.chat.id
			else:
				message.uid = 'C' + str(message.chat.id) + 'U' + str(message.from_user.id)
			tg_username = getattr(message.from_user, 'username', None)
			if tg_username == None:
				tg_username = getattr(message.from_user, 'first_name', '') + ' ' + getattr(message.from_user, 'last_name', '')
			chat_name = str(message.chat.title)

			if message.uid in srv.selected_games:
				gamename = srv.selected_games[message.uid].__name__
			else:
				gamename = ''

			if message.text.lower() == 'оживи' or  message.text.lower() == 'пих':
				reply = '💰🔮📿🤯🥸🤪🤣🍺🍻🍾🎮💻📱🖥🧻🔐🕉♌♋🔯✡️💮🉐㊙️㊙️㊗️🈴🈹🈹🈲🐛🐖🍀💥🌈🌪🐀🐁🐡🕸🙈'
			else:
				if message.uid not in srv.selected_games or message.text == '?': #если ещё не записано имя
					reply = EnterUrName.start(message)
					srv.selected_games[message.uid]=EnterUrName
				else:
					if message.text == '!':
						reply_func = srv.list_games
					else:
						reply_func = srv.selected_games[message.uid].reply
					reply = reply_func(message)

			bot.send_message(message.chat.id, reply)

			if message.uid in srv.data and 'username' in srv.data[message.uid]:
				username = srv.data[message.uid]['username']
			else:
				username = ''
			logging.info(str(message.uid) + ';' + tg_username + ';' + username + ';' + chat_name + ';' + gamename + ';' + repr(message.text) + ';' + repr(reply))

		except Exception as e:
			logging.warning(str(e) + ';' + str(e.args))
			if srv.get_config('RAISE_ERRORS'): raise e

	bot.polling(non_stop=True) #запускаем постоянную обработку сообщений

except Exception as e:
	logging.error(str(e) + ';' + str(e.args))
	#pass
	if srv.get_config('RAISE_ERRORS'): raise e