import telebot
import psycopg2
from config import host, user, db_name, password
from telebot import types
import datetime
bot = telebot.TeleBot('5794052782:AAHcThXFjptp1rZD_FCasKIJxmlF4UWeYAc')
DOCTORS_LIST = ["Терапевт", "Хирург", "Стоматолог", "Пульмонолог"]
chosen_doctor = ""

try:
    conn = psycopg2.connect(host=host,
                            user=user,
                            password=password,
                            database=db_name)
    conn.autocommit
except Exception as e:
    print("Error", e)


def choose_asap(message):
    markup = types.ReplyKeyboardMarkup()
    yes_btn = types.KeyboardButton("Да")
    no = types.KeyboardButton("Нет")
    markup.add(yes_btn, no)
    bot.send_message(message.chat.id, "Вы хотите записаться на ближайшую дату?", reply_markup=markup)


# Старт бота
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    choose_doctor = types.KeyboardButton("Выбрать специалиста")
    markup.add(choose_doctor)
    mess = f'Здравствуйте, <b>{message.from_user.first_name} <u>{message.from_user.last_name}</u></b>! ' \
           f'С помощью этого бота вы сможете записаться к врачу'
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


# Основной блок
@bot.message_handler()
def choose_specialist(message):
    global chosen_doctor
    # Выбор врача
    if message.text == "Выбрать специалиста" or message.text == "Вернуться к выбору специалистов":
        markup = types.ReplyKeyboardMarkup()
        therapist = types.KeyboardButton("Терапевт")
        pulmonologist = types.KeyboardButton("Пульмонолог")
        dentist = types.KeyboardButton("Стоматолог")
        surgeon = types.KeyboardButton("Хирург")
        markup.add(therapist, pulmonologist, dentist, surgeon)
        bot.send_message(message.chat.id, "Выберите специалиста к которому хотите записаться", reply_markup=markup)

    # Если указаный врач существует
    if message.text in DOCTORS_LIST:
        specialist = message.text
        chosen_doctor = message.text
        markup = types.ReplyKeyboardMarkup()
        appointment_asap = types.KeyboardButton("Записаться на ближайшее свободное время")
        watch_schedule_week = types.KeyboardButton("Посмотреть свободное время на этой неделе")
        watch_schedule_month = types.KeyboardButton("Посмотреть свободное время на месяц вперёд")
        return_to_spec = types.KeyboardButton("Вернуться к выбору специалистов")
        markup.add(appointment_asap, watch_schedule_week, watch_schedule_month, return_to_spec)
        bot.send_message(message.chat.id, f"Вы хотите записаться к {specialist}, выберите нужный вариант",
                         reply_markup=markup)

    # Если выбран терапевт и нажата кнопка записи на ближайшее время
    if message.text == "Записаться на ближайшее свободное время" and chosen_doctor == "Терапевт":
        with conn.cursor() as cursor:
            try:
                cursor.execute("SELECT appointment_time FROM therapist WHERE doctor_busy=FALSE LIMIT 1;")
                closest_time = cursor.fetchone()
                print(closest_time)
            except Exception as e:
                print("Error finding date",e)
        bot.send_message(message.chat.id, f"Ближайшая дата - {closest_time[0].strftime('%d-%m-%Y, %H:%M')}. Вам подходит этот вариант?")


bot.polling(non_stop=True)
