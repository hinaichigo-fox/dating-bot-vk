#дайвинчик 1.0. написан за 4 дня. если что-то не понятно пишите https://t.me/foxikusik
import random
import aiosqlite
import asyncio
import random
from aiohttp import TCPConnector
from vkbottle.bot import Bot, Message, BotLabeler
from vkbottle import API, Keyboard, Text, LoopWrapper
from vkbottle.http import SingleAiohttpClient


labeler = BotLabeler()
#авторизация бота. Сделал так потому что обычное не запускалось на VDSке(
async def main(loop_wrapper: LoopWrapper):
	bot = Bot(api=API(token="Ваш токен", http_client=SingleAiohttpClient(connector=TCPConnector(verify_ssl=False))), loop_wrapper=loop_wrapper, labeler=labeler)
	await bot.run_polling()



#Создание бд или если она есть подключение. БД из пунктов: Юзер айди, Имя, Город, Пол, О себе, Статус, Лайкает, Оценили, Аттач. Можете дополнить своими параметрами!
#про лайкает и Оценили будет расписано ниже(это важные параметры. оставьте их!)
#Статусы: 0 - меню 1 - юзер просматривает анкеты 2 - юзера лайкнули 4 - статус просмотра своей анкеты 5 - анкета отключена 
#Статусы: 17 - ваше имя 18 - ваш город 19 - ваш возраст 20 - ваш пол 21 - о себе 22 - аттач в анкету
#С 17 по 22 статусы относятся к анкете. Почему разброс такой? Потому что на гх публикую версию похожую на дайвинчик.
#Сам я писал бота для околополитов с расширенной анкетой где помимо имени города возраста пола и о себе были еще вопросы про ориентацию и полит взгляды и т.д.
async def init_db():
	async with aiosqlite.connect('anket.db') as db:
		await db.execute("""
			CREATE TABLE IF NOT EXISTS anket(
				user_id INT PRIMARY KEY,
				name TEXT,
				gorod TEXT,
				age INT,
				pol TEXT,
				o_sebe TEXT,
				status INT,
				liked INT,
				ocen INT,
				att TEXT
			)
		""")
		await db.commit()

async def update_user_status(user_id, status): #обновление статуса юзера 
	async with aiosqlite.connect('anket.db') as db:
		await db.execute('UPDATE anket SET status = ? WHERE user_id = ?', (status, user_id))
		await db.commit()

async def get_random_user(user_id): #случайный юзер
	async with aiosqlite.connect('anket.db') as db:
		cursor = await db.execute('''
			SELECT user_id 
			FROM anket 
			WHERE user_id != ? AND status IN (0, 1, 4) #статусы меню, просмотра анкет и просмотра своей анкеты. Другие статусы не добавлял чтоб избежать гемороя
			ORDER BY RANDOM()  #чтоб не тратить время на добавления двух и более лайков на одну анкету я просто исключил ее из поиска
			LIMIT 1
		''', (user_id,))
		result = await cursor.fetchone()
	if result:
		return result[0]
	return 0

async def update_user_ocen(user_id, ocen): #обновляет айди того кого оценивает юзер
	async with aiosqlite.connect('anket.db') as db:
		await db.execute('UPDATE anket SET ocen = ? WHERE user_id = ?', (ocen, user_id))
		await db.commit()

async def get_user_liked(user_id): #получает айди лайкнутого юзера
	async with aiosqlite.connect('anket.db') as db:
		cursor = await db.execute('SELECT liked FROM anket WHERE user_id = ?', (user_id,))
		result = await cursor.fetchone()
	if result:
		return result[0]
	return 0 

async def get_user_status(user_id): #получает статус юзера
	async with aiosqlite.connect('anket.db') as db:
		cursor = await db.execute('SELECT status FROM anket WHERE user_id = ?', (user_id,))
		result = await cursor.fetchone()
	if result:
		return result[0]
	return 0

async def get_user_att(user_id): #получает аттач анкеты
	async with aiosqlite.connect('anket.db') as db:
		cursor = await db.execute('SELECT att FROM anket WHERE user_id = ?', (user_id,))
		result = await cursor.fetchone()
	if result:
		return result[0]
	return 0

async def get_user_ocen(user_id): #получает айди того кого оценивает юзер
	async with aiosqlite.connect('anket.db') as db:
		cursor = await db.execute('SELECT ocen FROM anket WHERE user_id = ?', (user_id,))
		result = await cursor.fetchone()
		return result[0]

async def delete_user_survey(user_id): #удаляет юзера из бд
	async with aiosqlite.connect('anket.db') as db:
		await db.execute('DELETE FROM anket WHERE user_id = ?', (user_id,))
		await db.commit()

async def add_new_user(user_id): #добавляет юзера в бд
	async with aiosqlite.connect('anket.db') as db:
		await db.execute('''
			INSERT INTO anket (user_id, name, gorod, age, pol, o_sebe, status, liked, ocen, att)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		''', (user_id, None, None, 0, None, None, 0, 0, 0, None))
		await db.commit()

async def get_total_records(): #получает кол-во всех записей в бд
	async with aiosqlite.connect('anket.db') as db:
		cursor = await db.execute('SELECT COUNT(*) FROM anket')
		result = await cursor.fetchone()
	if result:
		return result[0] 
	return 0 

async def save_answer_to_db(user_id, key, answer): #сохраняет ответ в бд
	async with aiosqlite.connect('anket.db') as db:
		await db.execute(f'UPDATE anket SET {key} = ? WHERE user_id = ?', (answer, user_id))
		await db.commit()

async def get_user_survey(user_id): #получает анкету юзера
	async with aiosqlite.connect('anket.db') as db:
		cursor = await db.execute('SELECT * FROM anket WHERE user_id = ?', (user_id,))
		return await cursor.fetchone()


def format_survey(survey_data): #формирует анкету юзера
	formatted_survey = ""

	if survey_data[1]:
		formatted_survey += f"{survey_data[1]}"
	if survey_data[3]:
		formatted_survey += f", {survey_data[3]} лет"
	formatted_survey += "\n"
	if survey_data[2] and survey_data[2] != "0":
		formatted_survey += f"Город: {survey_data[2]}"
	formatted_survey += "\n"
	if survey_data[4]:
		formatted_survey += f"Пол: {survey_data[4]}\n"
	if survey_data[5] and survey_data[5] != "0":
		formatted_survey += f"О себе: {survey_data[5]}\n"

	return formatted_survey



async def send_message_to_user(message, user_id, message_text,attachment, keyboard): #отправляет смс юзеру
	await message.ctx_api.messages.send(
		user_id=user_id,          
		message=message_text,   
		attachment=attachment,  
		random_id=random.randint(1, 2147483647),
		keyboard=keyboard        
	)

async def send_message_to_user3(message, user_id, message_text, keyboard): #отправляет смс юзеру 
	await message.ctx_api.messages.send(
		user_id=user_id,          
		message=message_text,   
		random_id=random.randint(1, 2147483647),
		keyboard=keyboard        
	)

async def send_message_to_chat(message, message_text, attachment): #отправляет смс в беседу(вставьте в пир айди айди своей админ беседы)
	peer_id = 2000000000
	await message.ctx_api.messages.send(
		peer_id=peer_id,
		message=message_text,
		attachment=attachment,
		random_id=random.randint(1, 2147483647)
	)


async def send_message_to_user2(message, user_id, message_text, attachment): #отправляет смс юзеру
	await message.ctx_api.messages.send(
		user_id=user_id,          
		message=message_text,
		attachment=attachment,
		random_id=random.randint(1, 2147483647)       
	)





def create_initial_menu_keyboard(): #клава начала 
	keyboard = Keyboard(one_time=True)
	keyboard.add(Text("Заполнить анкету"))
	return keyboard


def create_main_menu_keyboard(): #клава меню
	keyboard = Keyboard(one_time=True)
	keyboard.add(Text("1"))
	keyboard.add(Text("2"))
	keyboard.add(Text("3"))
	return keyboard


def create_main_anket_keyboard(): #клава анкеты 
	keyboard = Keyboard(one_time=True)
	keyboard.add(Text("1"))
	keyboard.add(Text("2"))
	keyboard.add(Text("3"))
	return keyboard


def create_main_pol_keyboard(): #клава выбора пола
	keyboard = Keyboard(one_time=True)
	keyboard.add(Text("Мужской"))
	keyboard.add(Text("Женский"))
	return keyboard


def create_optional_question_keyboard(): #клава пропуска
	keyboard = Keyboard(one_time=True)
	keyboard.add(Text("Пропустить"))
	return keyboard


def create_yes_keyboard(): #клава да
	keyboard = Keyboard(one_time=True)
	keyboard.add(Text("Да"))
	return keyboard


def create_rating_keyboard(): #клава лайкинга
	keyboard = Keyboard(one_time=False)
	keyboard.add(Text("👍"))
	keyboard.add(Text("👎"))
	keyboard.add(Text("⚠"))
	keyboard.add(Text("💤"))
	return keyboard


def create_ocen_keyboard(): #клава взаимной симпатии
	keyboard = Keyboard(one_time=False)
	keyboard.add(Text("👍"))
	keyboard.add(Text("👎"))
	return keyboard


@labeler.message(text="Начать") #если смс начать
async def show_initial_menu(message: Message):
	user_id = message.from_id #берем юзер ид из смс
	survey_data = await get_user_survey(user_id) #получаем анкету
	if survey_data is None: #если анкеты нет
		total_records = await get_total_records() # получаем кол-во записей в бд и пишем смс
		await message.answer(f"Привет! Я Леонардо Дайвинчик. В моей базе уже {total_records} человек! Я помогу тебе найти друзей! Давай заполним анкету?", keyboard=create_initial_menu_keyboard())
	else: #если анкета есть
		await message.answer("Ошибка") #пишем ошибка 


@labeler.message(text="Заполнить анкету") #если смс заполнить анкету
async def start_survey(message: Message):
	user_id = message.from_id #получаем юзер ид из смс
	survey_data = await get_user_survey(user_id) #получаем анкету
	if survey_data is None: #если анкеты нет
		user_id = message.from_id #на всякий берем юзер ид из смс
		await add_new_user(user_id) #добавляем нового юзера
		await update_user_status(user_id, 17) #ставим статус первого вопроса в анкете 
		await message.answer("Как вас зовут?") #задаем вопрос
	else: #если анкета есть
		await message.answer("Анкета уже заполнена.") #анкета заполнена


@labeler.message(text=["Пропустить", "пропустить", "0", "-"]) #лист слов пропуска можете дополнить своими
async def skip_question(message: Message):
	user_id = message.from_id #получаем айди
	user_status = await get_user_status(user_id) #берем статус
	if user_status == 18: #если статус 18
		await save_answer_to_db(user_id, "gorod", "0") #сохраняем 0 в колонку город
		await update_user_status(user_id, 19) #обновляем статус
		await message.answer("Сколько вам лет?") #пишем вопрос
	if user_status == 21: #если статус 21
		await save_answer_to_db(user_id, "o_sebe", "0") #сохраняем 0 в колонку о себе
		await update_user_status(user_id, 22) #обновляем статус и просим аттач
		await message.answer("Пришли фото музыку или видео которое будет в анкете. 1 вложение! Другие вложения кроме фото, видео или музыки не принимаются!(Видео должно быть доступно всем!)")
	if user_status not in [18, 21]: #если статус не 18 или 21 то пишем ошибка
		await message.answer("Ошибка")

@labeler.message() #если шлют любое смс
async def handle_answer(message: Message):
	if message.text: #если в смс есть текст
		user_id = message.from_id #айди из смс
		user_status = await get_user_status(user_id) #получаем статус
		survey_data = await get_user_survey(user_id) #получаем анкету
		if survey_data is None: #если ее нет
			total_records = await get_total_records() #получаем кол-во записей и пишем смс
			await message.answer(f"Привет! Я Леонардо Дайвинчик. В моей базе уже {total_records} человек! Я помогу тебе найти друзей! Давай заполним анкету?", keyboard=create_initial_menu_keyboard())
		else: #если анкета есть
			user_id = message.from_id #айди из смс
			user_status = await get_user_status(user_id) #получаем статус
			if user_status == 17:  #если статус 17 то чекаем кол-во букв(можете вставить свое)
				if len(message.text) > 200:
					await message.answer("А не дофига ли буковок?")
				else: #если букв меньше 200
					await save_answer_to_db(user_id, "name", message.text) #сохраняем в колонку имя весь текст из смс
					await update_user_status(user_id, 18) #обновляем статус
					await message.answer("Из какого вы города?", keyboard = create_optional_question_keyboard()) #пишем следующий вопрос
			if user_status == 18: #та же фигня опять чек букв, обновление статуса и следующий вопрос
				if len(message.text) > 200:
					await message.answer("А не дофига ли буковок?")
				else:
					await save_answer_to_db(user_id, "gorod", message.text)
					await update_user_status(user_id, 19)
					await message.answer("Сколько вам лет?")					
			if user_status == 19: #та же фигня опять чек букв, обновление статуса и следующий вопрос
				try:
					let = int(message.text)
					if let < 1000:
						await save_answer_to_db(user_id, "age", let)
						await update_user_status(user_id, 20)
						await message.answer("Ваш пол?", keyboard = create_main_pol_keyboard())
					else: 
						await message.answer("Итить ты старый. Давай реальный возраст пиши.")
				except:
					await message.answer("Возраст нужно писать цифрами")
			if user_status == 20: #та же фигня опять чек букв, обновление статуса и следующий вопрос
				if len(message.text) > 200:
					await message.answer("А не дофига ли буковок?")
				else:
					await save_answer_to_db(user_id, "pol", message.text)
					await update_user_status(user_id, 21)
					await message.answer("Расскажите о себе.", keyboard = create_optional_question_keyboard())
			if user_status == 21: #та же фигня опять чек букв, обновление статуса и следующий вопрос
				if len(message.text) > 600:
					await message.answer("А не дофига ли буковок?")
				else:
					await save_answer_to_db(user_id, "o_sebe", message.text)
					await update_user_status(user_id, 22)
					await message.answer("Пришли фото музыку или видео которое будет в анкете. 1 вложение! Другие вложения кроме фото, видео или музыки не принимаются!(Видео должно быть доступно всем!)")
			if user_status == 0: #если статус 0 т.е. меню 
				if message.text == "1": #если смс 1 
					user_id = message.from_id #берем ид
					await update_user_status(user_id, 1) #обновляем статус на 1 
					random_user_id = await get_random_user(user_id) #берем рандомного юзера
					if random_user_id: #если он есть
						survey_data = await get_user_survey(random_user_id) #получаем анкету
						await update_user_ocen(user_id, random_user_id) #обновляем колонку ocen юзера т.е. записываем рандом айди юзера  
						formatted_survey = format_survey(survey_data) #формируем анкету
						attach = await get_user_att(random_user_id) #берем аттач
						await message.answer(f"{formatted_survey}", attachment=attach, keyboard = create_rating_keyboard()) #отправляем анкету
					else: #если анкет нет
						await update_user_status(user_id, 0) #сбрасываем статус на 0 и кидаем юзера в меню
						await message.answer(f"Нет доступных анкет. Вы переходите в меню \nЧто делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
				if message.text == "2": #если смс 2 
					user_id = message.from_id
					await update_user_status(user_id, 4) #обновляем статус
					survey_data = await get_user_survey(user_id) #берем анкету юзера
					formatted_survey = format_survey(survey_data) #формируем ее
					attach = await get_user_att(user_id) #берем аттач
					await message.answer(f"Ваша анкета:\n{formatted_survey}", attachment=attach) #кидаем ему анкету и пишем смс 
					await message.answer(f"Что делаем дальше? \n1. Заполнить анкету заново. \n2. Смотреть анкеты. \n3.  Вернуться в меню.", keyboard =  create_main_anket_keyboard())
				if message.text == "3": #если смс 3 
					await update_user_status(user_id, 5) #обновляем статус на 5 и пишем смс о том что отключили анкету
					await message.answer("Отключил вашу анкету. Хотите ее включить?", keyboard = create_yes_keyboard()) 
				if message.text not in ["1", "2", "3"]: #если смс не 1 2 3 то пишем что юзер ошибся
					await message.answer("Ошибка. Вы сейчас в меню.")
					await message.answer(f"Что делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
			if user_status == 1: #если статус 1 
				if message.text == "👍": #если смс лайк
					user_id = message.from_id
					b = await get_user_ocen(user_id) #получаем того кого оценил юзер 
					await save_answer_to_db(b, "liked", user_id) #сохраняем то что юзера оценил тот кто отправил лайк
					await update_user_status(b, 2) #ставим ему статус того что его лайкнули
					c = await get_user_survey(user_id) #получаем анкету юзера который лайкнул
					d = format_survey(survey_data) #формируем ее
					attach = await get_user_att(user_id) # получааем аттач и отправляем смс тому юзеру которого лайкнули о том что его лайкнули
					await send_message_to_user(message, b, f"Вас лайкнули \n{d}", attachment=attach, keyboard = create_ocen_keyboard())
					random_user_id = await get_random_user(user_id) #дальше получаем рандом юзера
					if random_user_id: #если он есть формируем анкету и аттач и кидаем анкету
						survey_data = await get_user_survey(random_user_id)
						await update_user_ocen(user_id, random_user_id)
						attach = await get_user_att(random_user_id)
						formatted_survey = format_survey(survey_data)
						await message.answer(f"{formatted_survey}", attachment=attach, keyboard = create_rating_keyboard())
					else: #если юзеров нет то кидаем в меню
						await update_user_status(user_id, 0)
						await message.answer(f"Нет доступных анкет. Вы переходите в меню \nЧто делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
				if message.text == "👎": #если смс диз берем айди получаем рандом юзера если он есть обновляем колонку того кого оценивает юзер и даем ему анкету
					user_id = message.from_id #если нет никого то кидаем в меню
					random_user_id = await get_random_user(user_id)
					if random_user_id:
						await update_user_ocen(user_id, random_user_id)
						survey_data = await get_user_survey(random_user_id)
						formatted_survey = format_survey(survey_data)
						attach = await get_user_att(random_user_id)
						await message.answer(f"{formatted_survey}", attachment=attach, keyboard = create_rating_keyboard())
					else:
						await update_user_status(user_id, 0)
						await message.answer(f"Нет доступных анкет. Вы переходите в меню \nЧто делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
				if message.text == "⚠": #жалоба на юзеров
					user_id = message.from_id
					b = await get_user_ocen(user_id) #получаем айди того на кого жалуются
					survey_data = await get_user_survey(b) #получаем анкету
					formatted_survey = format_survey(survey_data) #формируем 
					attach = await get_user_att(b) #получаем аттач(мб жалоба на него) и отправляем в админ чат жалобу с айди того кто пожаловался и того на кого поджаловались
					await send_message_to_chat(message, f"Жалоба от @id{user_id} на анкету @id{b} \n{formatted_survey}", attachment=attach)
					await message.answer(f"Жалоба была подана!", keyboard = create_rating_keyboard()) #отправляем юзеру что жалоба подана
					random_user_id = await get_random_user(user_id) #дальше берем новую анкету
					if random_user_id:
						await update_user_ocen(user_id, random_user_id)
						survey_data = await get_user_survey(random_user_id)
						formatted_survey = format_survey(survey_data)
						attach = await get_user_att(random_user_id)
						await message.answer(f"{formatted_survey}", attachment=attach, keyboard = create_rating_keyboard())
					else:
						await update_user_status(user_id, 0)
						await message.answer(f"Нет доступных анкет. Вы переходите в меню \nЧто делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
				if message.text == "💤": #если смс выход из оценки то кидаем в меню
					await update_user_status(user_id, 0)
					await message.answer(f"Что делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
				if message.text not in ["👍", "👎", "💤", "⚠"]: #если смс не равен лайку дизу жалобе или выходу пишем ошибку
					await message.answer("Ошибка. Вы сейчас смотрите анкеты.", keyboard =  create_rating_keyboard())
			if user_status == 2: #если юзера оценили 
				if message.text == "👍": #если он поставил лайк
					user_id = message.from_id 
					a = await get_user_liked(user_id) #получаем айди того кто его лайкнул
					survey_data2 = await get_user_survey(user_id) #получаем анкету юзера
					survey_data = await get_user_survey(a) #получаем анкету того кто лайкнул
					formatted_survey = format_survey(survey_data) #формируем анкету 
					formatted_survey2 = format_survey(survey_data2) #формируем вторую анкету
					attach1 = await get_user_att(a) #получаем аттач
					attach2 = await get_user_att(user_id) #получаем аттач
					await message.answer(f"У вас взаимная симпатия с @id{a} \n{formatted_survey}", attachment=attach1) #отправляем смс о взаимной симпатии
					await update_user_status(user_id, 0) #обновляем статус юзера на меню и пишем об этом. Второмуюзеру тоже пишем смс о взаимной симпатии и кидаем в меню.
					await send_message_to_user2(message, a, f"У вас взаимная симпатия с \n@id{user_id} \n{formatted_survey2}", attachment=attach2)
					await send_message_to_user3(message, a, f"Что делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", create_main_menu_keyboard())
					await message.answer(f"Что делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
				if message.text == "👎": #если смс дизлайк
					user_id = message.from_id
					await update_user_status(user_id, 0) #апдейтим статус на 0 и кидаем в меню
					await message.answer(f"Что делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
				if message.text not in ["👍", "👎"]: #если смс не лайк или диз то пишем ошибка
					await message.answer(f"Ошибка", keyboard =  create_ocen_keyboard())
			if user_status == 4: #если юзер смотрит свою анкету
				if message.text == "1": #если смс 1 то удаляем юзера и создаем нового апдейтим статус на 17 и спрашиваем имя
					user_id = message.from_id
					await delete_user_survey(user_id)
					await add_new_user(user_id)
					await update_user_status(user_id, 17)
					await message.answer("Как вас зовут?")
				if message.text == "2": #если смс 2 то апдейтим статус на 1 и даем анкету
					await update_user_status(user_id, 1)
					random_user_id = await get_random_user(user_id)
					if random_user_id:
						survey_data = await get_user_survey(random_user_id)
						await update_user_ocen(user_id, random_user_id)
						formatted_survey = format_survey(survey_data)
						attach1 = await get_user_att(random_user_id)
						await message.answer(f"{formatted_survey}", attachment = attach1, keyboard = create_rating_keyboard())
					else:
						await update_user_status(user_id, 0)
						await message.answer(f"Нет доступных анкет. Вы переходите в меню \nЧто делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
				if message.text == "3": #если смс 3 возвращаемся в меню
					await update_user_status(user_id, 0)
					await message.answer(f"Что делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
				if message.text not in ["1", "2", "3"]: #если смс не 1 2 3 то пишем ошибку
					await message.answer(f"Ошибка. Вы сейчас смотрите свою анкету.", keyboard =  create_ocen_keyboard())
			if user_status == 5: #если анкета отключена
				if message.text == "Да": #если юзер пишет да то включаем ее 
					await update_user_status(user_id, 0)
					await message.answer(f"Включил вашу анкету. Что делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard =  create_main_menu_keyboard())
				if message.text != "Да": #если смс отличное от да пишем юзеру что его анкета отлючена
					await message.answer("Ошибка. Ваша анкета сейчас отключена. Включить анкету?", keyboard = create_yes_keyboard())
	else:
		if message.attachments: #если в смс есть аттач
			user_id = message.from_id 
			user_status = await get_user_status(user_id)
			survey_data = await get_user_survey(user_id)
			if survey_data is None: #если нет анкеты пишем ошибка
				await message.answer("Ошибка")
			else: #если есть чекаем статус. если 22 то
				if user_status == 22:
					user_id = message.from_id #берем айди
					ms  = await message.get_full_message() #получаем все смс
					atts = ms.get_attachment_strings()[0] #берем первый аттач из всех(если хотите реализовать больше 1 аттача просто уберите [0])
					if 'photo' in atts or 'video' in atts or 'audio' in atts: #если аттач фото видео или аудио то хорошо. если другое то нет(документы ставить опасно потому что могут txt тоже кидать)
						user_id = message.from_id
						await save_answer_to_db(user_id, "att", str(atts)) #обновляем колонку аттачей
						await update_user_status(user_id, 0) #апдейтим статус юзера
						survey_data = await get_user_survey(user_id) #получаем анкету
						formatted_survey = format_survey(survey_data) #формируем ее
						attach = await get_user_att(user_id) #получаем аттач
						await message.answer(f"Ваша анкета:\n{formatted_survey}", attachment=attach) #кидаем анкету и кидаем в меню
						await message.answer(f"Что делаем дальше? \n1. Смотреть анкеты. \n2. Моя анкета. \n3. Я больше не хочу никого искать.", keyboard = create_main_menu_keyboard())

if __name__ == "__main__": #запуск бота
	asyncio.run(init_db()) #запуск анкеты
	loop_wrapper = LoopWrapper() #лупинг бота чтоб он вечно работал
	loop_wrapper.on_startup.append(main(loop_wrapper))
	loop_wrapper.run()