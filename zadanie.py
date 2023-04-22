import telebot
from telebot import types
import sqlite3
conn = sqlite3.connect("shops_001.db")
cursor = conn.cursor()

conn.close()
#cursor.execute("""CREATE TABLE IF NOT EXISTS SHOP_001 (id INTEGER PRIMARY KEY AUTOINCREMENT,
#name TEXT, category TEXT, kol INT, price INT,sklad  INT)""")

# Таблица для user

#cursor.execute("""CREATE TABLE IF NOT EXISTS USERS (id INTEGER PRIMARY KEY AUTOINCREMENT,
#name TEXT, password TEXT)""")

# Перемещение товара
#cursor.execute("""CREATE TABLE IF NOT EXISTS OTGRUZKA (id INTEGER PRIMARY KEY AUTOINCREMENT,
#name_product TEXT, city, name_user Text, kol INT)""")

bot = telebot.TeleBot('6295969605:AAH1cDLmjsndFKionE9wGdZcMWWcrIQEwTE')

@ bot.message_handler(commands=['старт'])
def start_sklad(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Привет, {name}')
    log = bot.send_message(message.chat.id, f'Введите ваш login и Password:')
    bot.register_next_step_handler(log, vvod_user)

def vvod_user(message):
        name = message.text.split(', ')
        conn = sqlite3.connect("shops_001.db")
        cursor = conn.cursor()

        z = proverku(name)

        if z == True:
            bot.send_message(message.chat.id, f'Пользователь существует')
            info(message)
        else:
            cursor.execute('''INSERT INTO USERS (name,password) VALUES (?,?)''',
                       (name[0], name[1]))
            conn.commit()
            bot.send_message(message.chat.id, f'Регистрация успешна прошла')
            info(message)
        conn.close()

def delit(a):
    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()
    z = cursor.execute(f'''SELECT * FROM SHOP_001 WHERE name = '{a[0]}'  ''')
    z = z.fetchall()
    print(z)
    num = int(z[0][3])-int(a[3])
    print(num)
    cursor.execute(f'''UPDATE SHOP_001 SET kol = {num} WHERE name = '{a[0]}' ''')
    conn.commit()
@bot.message_handler(commands=['info'])
def info (message):
    keyboard = types.InlineKeyboardMarkup()
    name_btn = types.InlineKeyboardButton(text = "По имени", callback_data = 'name')
    sklad_btn = types.InlineKeyboardButton(text="По складу", callback_data='sklad')
    category_btn = types.InlineKeyboardButton(text="По категории", callback_data='category')
    all_btn = types.InlineKeyboardButton(text="Вывести все", callback_data='out_put_all')
    add_product = types.InlineKeyboardButton(text="Добавить товар", callback_data='add_product')
    otgruz_product = types.InlineKeyboardButton(text="Отгрузка", callback_data='otgruzka')
    keyboard.row(name_btn,sklad_btn,category_btn,all_btn)
    keyboard.row(add_product)
    keyboard.row(otgruz_product)
    bot.send_message(message.chat.id,"Выберите фильтр",  reply_markup=keyboard)


@ bot.callback_query_handler(func=lambda call:True)
def call_back_worker(call):
    if call.data == 'name':
        sent = bot.send_message(call.message.chat.id, 'Сортируем по имени. Какой товар вас интересует?')
        bot.register_next_step_handler(sent,vvod_name)
    elif call.data == 'sklad':
        sent = bot.send_message(call.message.chat.id, 'Сортируем по складу. Выбираем склад(1,2 или 3)?')
        bot.register_next_step_handler(sent, vvod_sklad)
    elif call.data == 'category':
        sent = bot.send_message(call.message.chat.id, 'Сортируем по категории . Выбираем категорию?')
        bot.register_next_step_handler(sent, vvod_category)
    elif call.data == 'out_put_all':
        bot.send_message(call.message.chat.id, 'Наличие товара на всех складах:')
        conn = sqlite3.connect("shops_001.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM SHOP_001''')
        k = cursor.fetchall()
        #bot.send_message(call.message.chat.id, f'{k}')
        obertka(call.message, k)
        conn.close()
    elif call.data == 'add_product':
        add(call.message)

    elif call.data == 'otgruzka' :
        delete(call.message)

def obertka(message,a):
    for i in a:
        s = f'Имя: {i[1]},  Категория: {i[2]}, Остаток: {i[3]} шт. ,Цена: {i[4]} у.е ,Склад: {i[5]}'
        bot.send_message(message.chat.id, f'{s}')

def vvod_name(message):
    name = message.text
    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM SHOP_001 WHERE name = ?''',(name,))
    k = cursor.fetchall()
    #bot.send_message(message.chat.id, f'{k}')
    obertka(message, k)
    conn.close()
def vvod_sklad(message):
    sklad = int(message.text)
    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM SHOP_001 WHERE sklad = ?''', (sklad,))
    k = cursor.fetchall()
    #bot.send_message(message.chat.id, f'{k}')
    obertka(message, k)
    conn.close()
def vvod_category(message):
    category = message.text
    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM SHOP_001 WHERE category = ?''', (category,))
    k = cursor.fetchall()
    #bot.send_message(message.chat.id, f'{k}')
    obertka(message,k)
    conn.close()
@bot.message_handler(commands=['add'])
def add(message):

    name = bot.send_message(message.chat.id, f'Введи имя товара,категорию,количество,цену,склада:,')
    bot.register_next_step_handler(name, vvod_tovara)

@bot.message_handler(commands=['otgruzka'])
def delete(message):
    name = bot.send_message(message.chat.id, f'Введи наименование товара, город отгрузки, имя получателя, количество:,')
    bot.register_next_step_handler(name, otgruzka)

def otgruzka(message):
    tovar = message.text.split(', ')

    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()
    print(tovar)
    cursor.execute('''INSERT INTO OTGRUZKA (name_product,city,name_user,kol) VALUES (?,?,?,?)''',
                   (tovar[0], tovar[1], tovar[2], tovar[3]))
    conn.commit()
    conn.close()

    delit(tovar)


def vvod_tovara(message):
    tovar = message.text
    tovar = tovar.split(',')

    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO SHOP_001 (name,category,kol,price,sklad) VALUES (?,?,?,?,?)''',
                   (tovar[0], tovar[1], tovar[2],tovar[3],tovar[4]))

    conn.commit()
    print(tovar)
    conn.close()
def proverku(a):
    conn = sqlite3.connect("shops_001.db")
    cursor = conn.cursor()
    z = cursor.execute(f'''SELECT * FROM USERS WHERE name = '{a[0]}' and password = '{a[1]}' ''')
    z = z.fetchall()

    if len(z) == 0:
         return False
    else:
         return True

conn.close()



bot.polling(non_stop=True)





