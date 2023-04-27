import random
import sqlite3
import time
import webbrowser
from datetime import date

import telebot
from telebot import types

from config import *

# //////////////////////////////////////////////////////////////////////////////////////////////////////
# *---------------------------------------- Application -----------------------------------------------*
# /////////////////////////////////////////////////////////////////////////////////////////////////////

# <<<<<<<<<<<<<<<< Переменные >>>>>>>>>>>>>>>>>
bot = telebot.TeleBot(BOT_TOKEN)


def first_visit(message, user_name):
    con = sqlite3.connect('files/database.sqlite')
    cur = con.cursor()
    cur.execute(f"update user_info set do_play = 'yes'")
    con.commit()

    bot.send_message(message.from_user.id,
                     f'Добро пожаловать в дневник снов, {user_name}!')
    bot.send_message(message.from_user.id, TEXT_what_is_it)
    bot.send_message(message.from_user.id,
                     'Если я тебя заинтересовал, то давай продолжим? :)',
                     reply_markup=marcup_start)


def start_conversation(message, user_name):
    bot.send_message(message.from_user.id, f'Привет, {user_name}!',
                     reply_markup=marcup_start)


@bot.message_handler(commands=['start'])
def start(message):
    con = sqlite3.connect('files/database.sqlite')
    cur = con.cursor()
    cur.execute(
        "create table if not exists user_dreams(dream_name text, dream_story text, dream_notes text, dream_category text, dream_phase text, dream_date text)")
    cur.execute("create table if not exists user_info(do_play text)")
    cur.execute(f"INSERT INTO user_info(do_play) VALUES('no')")
    con.commit()
    do_play = cur.execute('select do_play from user_info').fetchall()
    user_name = message.from_user.first_name

    if do_play[0][0] == "yes":
        start_conversation(message, user_name)
    else:
        first_visit(message, user_name)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() in ['* новый сон *', 'сон']:
        with open('files/broker.txt', 'w', encoding='utf-8') as file:
            file.write('')

        bot.send_message(message.from_user.id,
                         'Хорошо, давай запишем новое сновидение!')
        sent = bot.send_message(message.from_user.id,
                                'Скажи, пожалуйста, как ты назавешь свой сон:')
        bot.register_next_step_handler(sent, add_dream_name)

    elif message.text.lower() in ['* история снов *', 'история', 'все сны',
                                  'сны']:
        history(message)

    elif message.text.lower() in ['* меню *', 'меню']:
        marcup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        marcup.add(types.KeyboardButton('* Сброс'))
        bot.send_message(message.from_user.id, 'Вернул в меню 🌙',
                         reply_markup=marcup_start)

    elif message.text.lower() in ['* для чего нужен дневник снов? *',
                                  'что это', 'что это?']:
        bot.send_message(message.from_user.id, TEXT_what_is_it, reply_markup=marcup_start)

    elif message.text.lower() in ['* сброс *', 'сброс', 'сбросить']:
        marcup = types.InlineKeyboardMarkup()
        marcup.add(
            types.InlineKeyboardButton(text='✅', callback_data='**delete'),
            types.InlineKeyboardButton(text='❌', callback_data='**no_delete'))
        bot.send_message(message.from_user.id,
                         '⚠️ Ты уверен, что хочешь удалить всю историю своих сновидений?️',
                         reply_markup=marcup)
    elif message.text.lower == '* что такое фаза (осознанные сновидения)? *':
        bot.send_message(message.from_user.id, 'Перенаправление на сайт... ➡️')
        webbrowser.open(
            'https://trends.rbc.ru/trends/social/625ff3129a794715283cdc6a',
            new=2)

    else:
        bot.send_message(message.from_user.id,
                         'Извини, но я тебя не понял :(\nВот доступные команды ➡',
                         reply_markup=marcup_start)


def add_dream_name(message):
    cur = sqlite3.connect('files/database.sqlite').cursor()
    names = cur.execute('select dream_name from user_dreams').fetchall()

    while True:
        if message.text.count('*') == 2:
            sent = bot.send_message(message.from_user.id,
                                    'В названии сна не может быть 2 знака "*", пожалуйста, введи другое название сна:')
            bot.register_next_step_handler(sent, add_dream_name)
            break
        elif message.text.capitalize() in [i[0] for i in names]:
            sent = bot.send_message(message.from_user.id,
                                    'У вас уже есть сон с таким же названием, пожалуйста, переименуйте сновидение:')
            bot.register_next_step_handler(sent, add_dream_name)
            break
        else:
            write_to_broker(message.text)
            sent = bot.send_message(message.from_user.id, 'Какой сюжет:')
            bot.register_next_step_handler(sent, add_dream_story)
            break


def add_dream_story(message):
    write_to_broker(message.text)
    sent = bot.send_message(message.from_user.id,
                            'Введи ключевые моменты, которые пригодятся в будущем для анализе сна:')
    bot.register_next_step_handler(sent, add_dream_notes)


def add_dream_notes(message):
    write_to_broker(message.text)
    sent = bot.send_message(message.from_user.id, 'Выбери категорию сна:',
                            reply_markup=marcup_category)
    bot.register_next_step_handler(sent, add_dream_category)


def add_dream_category(message):
    write_to_broker(message.text)
    sent = bot.send_message(message.from_user.id, 'Был ли осознанный сон:',
                            reply_markup=marcup_phase)
    bot.register_next_step_handler(sent, add_dream_phase)


def add_dream_phase(message):
    write_to_broker(message.text)
    bot.send_photo(message.from_user.id, random.choice(images))
    bot.send_message(message.from_user.id, 'Отлично, ваш сон сохранён!',
                     reply_markup=marcup_start)

    with open('files/broker.txt', encoding='utf-8') as file:
        dream_name, dream_story, dream_notes, dream_category, dream_phase = file.read().split(
            '</next>')[:-1]
    current_date = date.today()
    con = sqlite3.connect('files/database.sqlite')
    cur = con.cursor()
    cur.execute(
        f"insert into user_dreams (dream_name, dream_story, dream_notes, dream_category, dream_phase, dream_date) values ('{dream_name}', '{dream_story}', '{dream_notes}', '{dream_phase}', '{dream_category}', '{current_date}')")
    con.commit()


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    req = call.data
    bot.delete_message(call.message.chat.id, call.message.message_id)

    con = sqlite3.connect('files/database.sqlite')
    cur = con.cursor()
    all_dreams = cur.execute('select dream_name from user_dreams').fetchall()

    marcup = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton(text='меню',
                                          callback_data='**menu')
    button_2 = types.InlineKeyboardButton(text='история',
                                          callback_data='**history')
    button_3 = types.InlineKeyboardButton(text='изменить',
                                          callback_data='**update')
    button_4 = types.InlineKeyboardButton(text='удалить',
                                          callback_data='**delete_all')
    marcup.add(button_1, button_2, button_4, button_3)

    if req == '**menu':
        menu(call)
    elif req == '**history':
        history(call)

    elif req == '**delete_all':
        marcup = types.InlineKeyboardMarkup()
        marcup.add(
            types.InlineKeyboardButton(text='✅',
                                       callback_data='**delete_dream'),
            types.InlineKeyboardButton(text='❌',
                                       callback_data='**no_delete_dream'))
        bot.send_message(call.from_user.id,
                         '⚠ Ты правда хочешь удалить этот чудесный сон?',
                         reply_markup=marcup)
    elif req == '**delete_dream':
        with open('files/broker.txt', encoding='utf-8') as file:
            dream_name = file.read()
        with open('files/broker.txt', 'w') as file:
            file.write('')
        cur.execute(
            f'delete from user_dreams where dream_name == "{dream_name}"')
        con.commit()
        bot.send_message(call.from_user.id,
                         f'Сон "{dream_name}" успешно удалён!')
        history(call)
    elif req == '**no_delete_dream':
        history(call)

    elif req == '**delete':
        con = sqlite3.connect('files/database.sqlite')
        cur = con.cursor()
        cur.execute('delete from user_dreams')
        cur.execute('delete from user_info')
        con.commit()
        bot.send_message(call.from_user.id,
                         'Твоя история удалена!')
        menu(call)
    elif req == '**no_delete':
        menu(call)
    elif req == '**update':
        marcup = types.InlineKeyboardMarkup()
        marcup.add(
            types.InlineKeyboardButton(text='название',
                                       callback_data='change**dream_name'),
            types.InlineKeyboardButton(text='сюжет',
                                       callback_data='change**dream_story'),
            types.InlineKeyboardButton(text='фаза',
                                       callback_data='change**dream_phase'),
            types.InlineKeyboardButton(text='ключевые моменты',
                                       callback_data='change**dream_notes'))

        bot.send_message(call.from_user.id,
                         'Что ты хочешь изменить?',
                         reply_markup=marcup)
    elif 'change**' in req:
        with open('files/broker.txt', encoding='utf-8') as file:
            name = file.read()
        param = req.replace('change**', '')

        with open('files/broker2.txt', 'w', encoding='utf-8') as file:
            file.write(name + '</next>' + param)

        sent = bot.send_message(call.from_user.id, 'Меняй:')
        bot.register_next_step_handler(sent, dream_update)

    else:
        for dream in all_dreams:
            if dream[0] == req:
                dream_info = cur.execute(
                    f'select * from user_dreams where dream_name == "{req}"').fetchall()
                os = '✅' if dream_info[0][3].lower() in ['да',
                                                         'конечно'] else '❌'
                print(dream_info)
                bot.send_message(call.from_user.id,
                                 f'💤 \t <i>{dream_info[0][0]}</i> \t 💤 \n\n <b>➙ Сюжет: \t </b> {dream_info[0][1]} \n\n <b>➙ Ключевые моменты: \t </b> {dream_info[0][2]} \n\n <b>➙ Категоря: \t </b> {dream_info[0][4]} \n\n <b>➙ Осознанный сон: \t </b> {os} \n\n {dream_info[0][5]}',
                                 parse_mode='html', reply_markup=marcup)
                with open('files/broker.txt', 'w', encoding='utf-8') as file:
                    file.write(req)
                break


def history(message):
    con = sqlite3.connect('files/database.sqlite')
    cur = con.cursor()
    all_dreams = cur.execute('select dream_name from user_dreams').fetchall()

    marcup = types.InlineKeyboardMarkup()
    for dream in all_dreams:
        button = types.InlineKeyboardButton(text=dream[0],
                                            callback_data=dream[0])
        marcup.add(button)
    if len(all_dreams) != 0:
        bot.send_message(message.from_user.id,
                         f'Количество сохранённых снов: <i>{len(all_dreams)}</i>',
                         reply_markup=marcup, parse_mode="html")
    else:
        bot.send_message(message.from_user.id, f'Твой дневник снов пуст',
                         reply_markup=marcup_start)


def menu(message):
    bot.send_message(message.from_user.id, 'Лови меню',
                     reply_markup=marcup_start)


def dream_update(message):
    with open('files/broker2.txt', encoding='utf-8') as file:
        name, param = file.read().split('</next>')
        print(name, param)
    con = sqlite3.connect('files/database.sqlite')
    cur = con.cursor()
    cur.execute(
        f'update user_dreams set "{param}" = "{message.text}" where dream_name == "{name}"')
    con.commit()
    bot.send_message(message.from_user.id, 'Готово!')
    history(message)


bot.polling(none_stop=True, interval=0)
