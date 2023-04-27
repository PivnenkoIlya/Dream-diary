from telebot import types

BOT_TOKEN = '6050084462:AAH_ZR51IknX0J2b_DCDMbGTS3u2P0GZE00'

# ------------------ переменные ------------------
TEXT_what_is_it = """
Мало кто из нас записывает свои сновидения, а ведь это настолько просто... Но зачем всё это нужно?

1) Улучшается сновидческая память!

2) По мере улучшения памяти, вы начнёте запоминать сюжет все лучше и лучше. Это даёт вам возможность извлекать из снов замечательные идеи, которые способны кардинально изменить вашу жизнь!

3) Сны становятся ярче, реалистичнее и интереснее!

4) Самое главное - вы научитесь выходить в осознанный сон, то есть попадать в пространство, в котором возможно всё: от проходов сквозь стену до познания себя и окружаещего мира!
"""
images = [
    'https://img3.akspic.ru/crops/1/7/0/1/7/171071/171071-derevo_pod_nochnym_nebom-derevo-noch-zvezda-atmosfera-1920x1080.jpg',
    'https://img3.akspic.ru/crops/1/7/0/1/7/171071/171071-derevo_pod_nochnym_nebom-derevo-noch-zvezda-atmosfera-1920x1080.jpg',
    'https://img3.akspic.ru/crops/4/5/5/5/3/135554/135554-polumesyac-nebesnoe_yavlenie-luna-estestvennyj_sputnik-sobytie-1920x1080.jpg',
    'https://img2.akspic.ru/crops/0/2/1/5/6/165120/165120-stiv_yablonski_tessa-tessa-noch-voda-oblako-1920x1080.jpg',
    'https://img3.akspic.ru/previews/1/0/5/6/6/166501/166501-mikael_gustafsson_malenkaya_pamyat-oblako-rastenie-atmosfera-voda-x750.jpg',
    'https://img3.akspic.ru/previews/4/4/0/9/69044/69044-priroda-okean-more-gorizont-maldivy-x750.jpg',
    'https://img1.akspic.ru/previews/1/6/4/8/6/168461/168461-vash_nacionalnyj_les-les-priroda-voda-atmosfera-x750.jpg',
    'https://img1.akspic.ru/previews/8/9/2/9/99298/99298-zakat-bereg-plyazh-voda-tropicheskaya_zona-x750.jpg']

# ------------------ кнопки ------------------
marcup_start = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1,
                                         one_time_keyboard=True)
button_1 = types.KeyboardButton("* новый сон *")
button_2 = types.KeyboardButton('* история снов *')
button_3 = types.KeyboardButton('* для чего нужен дневник снов? *')
button_4 = types.KeyboardButton('* что такое фаза (осознанные сновидения)? *')
button_5 = types.KeyboardButton('* сброс *')
marcup_start.add(button_1, button_2, button_3, button_4, button_5)

marcup_category = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1,
                                            one_time_keyboard=True)
button_1 = types.KeyboardButton("Веселый 😄")
button_2 = types.KeyboardButton('Грустный 🙁')
button_3 = types.KeyboardButton('Заставляет задуматься 🤔')
button_4 = types.KeyboardButton('Новая идея 💡')
marcup_category.add(button_1, button_2, button_3, button_4)

marcup_phase = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = types.KeyboardButton("Да")
button_2 = types.KeyboardButton('Нет')
marcup_phase.add(button_1, button_2)


# ------------------ функции ------------------
def write_to_broker(text):
    with open('files/broker.txt', encoding='utf-8') as file:
        data = file.read() + text.capitalize() + '</next>'
    with open('files/broker.txt', 'w', encoding='utf-8') as file:
        file.write(data)
