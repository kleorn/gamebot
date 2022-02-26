#pip install pyTelegramBotAPI
#/home/admin/web/kan.01sh.ru/private/max_hippo_bot# cd /home/admin/web/kan.01sh.ru/private/max_hippo_bot && python3 bot.py
import os
if os.path.exists('config_secret.py'):
	import config_secret as config
else:
	import config
import telebot

class GameServer:
	def __init__(self):
		self.selected_games = {}
		self.games = []
		self.games = [
			{'func': KupiSlonaGame, 'num': '1', 'name': 'Купи слона'},
			{'func': MulTableGame, 'num': '2', 'name': 'Таблица умножения'}
		]

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
			return 'Приготовься! Начинаем игру \"' + game['name'] + '\"\nДля возврата к выбору игры отправь \"!\"'


class KupiSlonaGame(Game): #статический класс
	data = {}
	def reply(message):
		return 'Все говорят \"' + message.text + '\", а ты купи слона'

class MulTableGame(Game):
	data = {}
	def reply(message):
		return 'Все говорят \"' + message.text + '\", а ты поменяешь дерево на овцу?'

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