import telebot
import psycopg2
from config import host, user, db_name, password
from telebot import types
import datetime
from sql_mapping import sql_mapping


bot = telebot.TeleBot('5794052782:AAHcThXFjptp1rZD_FCasKIJxmlF4UWeYAc')
DOCTORS_LIST = ["Терапевт", "Хирург", "Стоматолог", "Пульмонолог"]
chosen_doctor = ""
closest_time = None

#Подключение базы данных
try:
    conn = psycopg2.connect(host=host,
                            user=user,
                            password=password,
                            database=db_name)
    conn.autocommit = True
except Exception as e:
    print("Error", e)


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
    if message.text in DOCTORS_LIST or message.text == "Нет, выбрать другой вариант":
        if message.text in DOCTORS_LIST:
            chosen_doctor = message.text
        else:
            pass
        markup = types.ReplyKeyboardMarkup()
        appointment_asap = types.KeyboardButton("Записаться на ближайшее свободное время")
        watch_schedule_week = types.KeyboardButton("Посмотреть свободное время на этой неделе")
        watch_schedule_month = types.KeyboardButton("Посмотреть свободное время на месяц вперёд")
        return_to_spec = types.KeyboardButton("Вернуться к выбору специалистов")
        markup.add(appointment_asap, watch_schedule_week, watch_schedule_month, return_to_spec)
        bot.send_message(message.chat.id, f"Вы хотите записаться к {chosen_doctor}, выберите нужный вариант",
                         reply_markup=markup)

    # Если выбран врач и нажата кнопка записи на ближайшее время
    if message.text == "Записаться на ближайшее свободное время":
        global closest_time
        markup_accept = types.ReplyKeyboardMarkup()
        yes = types.KeyboardButton("Да")
        no = types.KeyboardButton("Нет, выбрать другой вариант")
        markup_accept.add(yes, no)
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    f"SELECT appointment_time FROM {sql_mapping(chosen_doctor)} WHERE doctor_busy=FALSE LIMIT 1;")
                closest_time = cursor.fetchone()
            except Exception as e:
                print("Error finding date", e)
        bot.send_message(message.chat.id,
                         f"Ближайшая дата - {closest_time[0].strftime('%d-%m-%Y, %H:%M')}. Вам подходит этот вариант?",
                         reply_markup=markup_accept)

    if message.text == "Да":
        msg = bot.send_message(message.chat.id, "Как вас зовут?(Фамилия Имя)")
        bot.register_next_step_handler(msg,get_full_name)
#Запись имени в базу
def get_full_name(message):
    name = message.text.split()
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                f"UPDATE {sql_mapping(chosen_doctor)} SET patient_last_name = '{name[0]}', patient_first_name = '{name[1]}' "
                f"WHERE appointment_time = '{closest_time[0]}'")
        except Exception as e:
            print("Error inserting patient", e)
        finally:
            print("success")

bot.polling(non_stop=True)
