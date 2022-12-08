import telebot
import psycopg2
import itertools as it
from config import host, user, db_name, password
from telebot import types
from sql_mapping import sql_mapping

bot = telebot.TeleBot('5794052782:AAHcThXFjptp1rZD_FCasKIJxmlF4UWeYA')
DOCTORS_LIST = ["Терапевт", "Хирург", "Стоматолог", "Пульмонолог"]
chosen_doctor = ""  # Выбранный врач
closest_time = None  # Ближайшее время
week_time = None  # Список свободных дат в интервале недели в формате timestamptz
week_schedule_buttons = []  # Список кнопок с датами на неделю
chosen_time = ""  # Выбранное время
therapist_appointment_sql = None
dentist_appointment_sql = None
surgeon_appointment_sql = None
therapist_time = []
surgeon_time = []
dentist_time = []
therapist_markup = []
dentist_markup = []
surgeon_markup = []
therapist_print = ""
dentist_print = ""
surgeon_print = ""
phone = ""  # Номер телефона
button_pressed = False
new_appointment = False
index = None
# Подключение базы данных
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
    watch_my_appointments = types.KeyboardButton("Посмотреть мои записи")
    cancel_appointment = types.KeyboardButton("Отменить запись")
    markup.add(choose_doctor, watch_my_appointments, cancel_appointment)
    mess = f'Здравствуйте, <b>{message.from_user.first_name} <u>{message.from_user.last_name}</u></b>! ' \
           f'С помощью этого бота вы сможете записаться к врачу'
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


# Основной блок
@bot.message_handler()
def choose_specialist(message):
    global chosen_doctor
    global chosen_time
    global therapist_appointment_sql
    global dentist_appointment_sql
    global surgeon_appointment_sql
    global therapist_time
    global surgeon_time
    global dentist_time
    global therapist_print
    global dentist_print
    global surgeon_print
    global button_pressed
    global new_appointment
    global therapist_markup
    global dentist_markup
    global surgeon_markup

    if message.text == "Главное меню":
        start(message)

    # ///////////////////////////////////ПРОСМОТР ЗАПИСЕЙ ПОЛЬЗОВАТЕЛЯ/////////////////////////////////////////////////
    if message.text == "Посмотреть мои записи":
        telegram_id = message.from_user.id
        if button_pressed is True and new_appointment is False:
            bot.send_message(message.chat.id,
                             f"{message.from_user.first_name} {message.from_user.last_name}, "
                             f"ваши записи: \nТерапевт:\n{therapist_print},\n"
                             f"Стоматолог:\n{dentist_print},\n"
                             f"Хирург:\n{surgeon_print}")
        else:
            button_pressed = True
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        f"SELECT appointment_time FROM therapist WHERE  telegram_id = {telegram_id}"
                    )
                    therapist_appointment_sql = cursor.fetchall()
                    cursor.execute(
                        f"SELECT appointment_time FROM dentist WHERE  telegram_id = {telegram_id}"
                    )
                    dentist_appointment_sql = cursor.fetchall()
                    cursor.execute(
                        f"SELECT appointment_time FROM surgeon WHERE  telegram_id = {telegram_id}"
                    )
                    surgeon_appointment_sql = cursor.fetchall()
                except Exception as ex:
                    print("Error fetching data", ex)
            for tt, st, dt in it.zip_longest(therapist_appointment_sql, surgeon_appointment_sql,
                                             dentist_appointment_sql):
                if tt is None or tt[0].strftime('%d-%m-%Y, %H:%M') in therapist_time:
                    pass
                else:
                    therapist_time.append(tt[0].strftime('%d-%m-%Y, %H:%M'))
                if st is None or st[0].strftime('%d-%m-%Y, %H:%M') in surgeon_time:
                    pass
                else:
                    surgeon_time.append(st[0].strftime('%d-%m-%Y, %H:%M'))
                if dt is None or dt[0].strftime('%d-%m-%Y, %H:%M') in dentist_time:
                    pass
                else:
                    dentist_time.append(dt[0].strftime('%d-%m-%Y, %H:%M'))
            if len(therapist_time) > 0:
                therapist_print = '\n'.join(therapist_time)
            else:
                therapist_print = "Нет записи"
            if len(dentist_time) > 0:
                dentist_print = '\n'.join(dentist_time)
            else:
                dentist_print = "Нет записи"
            if len(surgeon_time) > 0:
                surgeon_print = '\n'.join(surgeon_time)
            else:
                surgeon_print = "Нет записи"
            new_appointment = False
            bot.send_message(message.chat.id,
                             f"{message.from_user.first_name} {message.from_user.last_name}, "
                             f"ваши записи: \nТерапевт:\n{therapist_print},\n"
                             f"Стоматолог:\n{dentist_print},\n"
                             f"Хирург:\n{surgeon_print}")

    # ////////////////////////////////////////////ОТМЕНА ЗАПИСИ/////////////////////////////////////////////////////////
    if message.text == "Отменить запись":
        telegram_id = message.from_user.id
        markup = types.ReplyKeyboardMarkup()
        markup.add("Главное меню")

        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    f"SELECT appointment_time FROM therapist WHERE  telegram_id = {telegram_id}"
                )
                therapist_appointment_sql = cursor.fetchall()
                cursor.execute(
                    f"SELECT appointment_time FROM dentist WHERE  telegram_id = {telegram_id}"
                )
                dentist_appointment_sql = cursor.fetchall()
                cursor.execute(
                    f"SELECT appointment_time FROM surgeon WHERE  telegram_id = {telegram_id}"
                )
                surgeon_appointment_sql = cursor.fetchall()
            except Exception as ex:
                print("Error fetching data", ex)
        for tt in therapist_appointment_sql:
            if tt is not None:
                markup.add(f"Терапевт: {tt[0].strftime('%d-%m-%Y, %H:%M')}")
                therapist_markup.append(f"Терапевт: {tt[0].strftime('%d-%m-%Y, %H:%M')}")
            else:
                pass
        for dt in dentist_appointment_sql:
            if dt is not None:
                markup.add(f"Стоматолог: {dt[0].strftime('%d-%m-%Y, %H:%M')}")
                dentist_markup.append(f"Стоматолог: {dt[0].strftime('%d-%m-%Y, %H:%M')}")
            else:
                pass
        for st in surgeon_appointment_sql:
            if st is not None:
                markup.add(f"Хирург: {st[0].strftime('%d-%m-%Y, %H:%M')}")
                surgeon_markup.append(f"Хирург: {st[0].strftime('%d-%m-%Y, %H:%M')}")
            else:
                pass
        bot.send_message(message.chat.id, "Выберите, какой визит отменить", reply_markup=markup)

    if message.text in therapist_markup or message.text in dentist_markup or message.text in surgeon_markup:
        if message.text in therapist_markup:
            cancel_therapist = therapist_appointment_sql[therapist_markup.index(message.text)]
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        f"UPDATE therapist SET patient_last_name = NULL, "
                        f"patient_first_name = NULL, "
                        f"patient_phone = NULL, "
                        f"telegram_id = NULL, "
                        f"doctor_busy = FALSE "
                        f"WHERE appointment_time='{cancel_therapist[0]}'"
                    )
                except Exception as ex:
                    print("Error cancelling therapist", ex)
                finally:
                    new_appointment = True
                    bot.send_message(message.chat.id, "Запись к терапевту успешно отменена")
                    start(message)
    if message.text in dentist_markup:
        cancel_dentist = dentist_appointment_sql[dentist_markup.index(message.text)]
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    f"UPDATE dentist SET patient_last_name = NULL, "
                    f"patient_first_name = NULL, "
                    f"patient_phone = NULL, "
                    f"telegram_id = NULL, "
                    f"doctor_busy = FALSE "
                    f"WHERE appointment_time='{cancel_dentist[0]}'"
                )
            except Exception as ex:
                print("Error cancelling dentist", ex)
            finally:
                new_appointment = True
                bot.send_message(message.chat.id, "Запись к стоматологу успешно отменена")
                start(message)
    if message.text in surgeon_markup:
        cancel_surgeon = surgeon_appointment_sql[surgeon_markup.index(message.text)]
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    f"UPDATE surgeon SET patient_last_name = NULL, "
                    f"patient_first_name = NULL, "
                    f"patient_phone = NULL, "
                    f"telegram_id = NULL, "
                    f"doctor_busy = FALSE "
                    f"WHERE appointment_time='{cancel_surgeon[0]}'"
                )
            except Exception as ex:
                print("Error cancelling surgeon", ex)
            finally:
                new_appointment = True
                bot.send_message(message.chat.id, "Запись к хирургу успешно отменена")
                start(message)
    # ////////////////////////////////////////////ВЫБОР ВРАЧА///////////////////////////////////////////////////////////
    if message.text == "Выбрать специалиста" or message.text == "Вернуться к выбору специалистов":
        markup = types.ReplyKeyboardMarkup()
        therapist = types.KeyboardButton("Терапевт")
        pulmonologist = types.KeyboardButton("Пульмонолог")
        dentist = types.KeyboardButton("Стоматолог")
        surgeon = types.KeyboardButton("Хирург")
        main_menu = types.KeyboardButton("Главное меню")
        markup.add(therapist, pulmonologist, dentist, surgeon, main_menu)
        bot.send_message(message.chat.id, "Выберите специалиста к которому хотите записаться", reply_markup=markup)

    # ////////////////////////////////ЕCЛИ ВРАЧ СУЩЕСТВУЕТ ИЛИ ВРЕМЯ НЕ ПОДХОДИТ////////////////////////////////////////
    if message.text in DOCTORS_LIST or message.text == "Нет, выбрать другой вариант":
        if message.text in DOCTORS_LIST:
            chosen_doctor = message.text
        else:
            pass
        markup = types.ReplyKeyboardMarkup()
        appointment_asap = types.KeyboardButton("Записаться на ближайшее свободное время")
        watch_schedule_week = types.KeyboardButton("Посмотреть свободное время на этой неделе")
        return_to_spec = types.KeyboardButton("Вернуться к выбору специалистов")
        markup.add(appointment_asap, watch_schedule_week, return_to_spec)
        bot.send_message(message.chat.id, f"Вы хотите записаться к {chosen_doctor}, выберите нужный вариант",
                         reply_markup=markup)

    # //////////////////////////////////////////ЗАПИСЬ НА БЛИЖАЙШЕЕ ВРЕМЯ///////////////////////////////////////////////
    if message.text == "Записаться на ближайшее свободное время":
        global closest_time
        markup_accept = types.ReplyKeyboardMarkup()
        yes = types.KeyboardButton("Да")
        no = types.KeyboardButton("Нет, выбрать другой вариант")
        markup_accept.add(yes, no)

        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    f"SELECT appointment_time FROM {sql_mapping(chosen_doctor)} "
                    f"WHERE doctor_busy=FALSE and appointment_time > CURRENT_TIMESTAMP "
                    f"ORDER BY appointment_time asc LIMIT 1;")
                closest_time = cursor.fetchone()
                chosen_time = closest_time
            except Exception as ex:
                print("Error finding date", ex)
        bot.send_message(message.chat.id,
                         f"Ближайшая дата - {closest_time[0].strftime('%d-%m-%Y, %H:%M')}. Вам подходит этот вариант?",
                         reply_markup=markup_accept)
    # /////////////////////////////////////////ПОСМОТРЕТЬ ВРЕМЯ НА ЭТОЙ НЕДЕЛЕ//////////////////////////////////////////
    if message.text == "Посмотреть свободное время на этой неделе":
        global week_time
        week_markup = types.ReplyKeyboardMarkup()
        no = types.KeyboardButton("Нет, выбрать другой вариант")
        week_markup.add(no)

        with conn.cursor() as cursor:
            try:
                cursor.execute(f"SELECT appointment_time FROM {sql_mapping(chosen_doctor)} "
                               f"WHERE doctor_busy=FALSE and appointment_time>=CURRENT_TIMESTAMP "
                               f"AND appointment_time<=CURRENT_TIMESTAMP + INTERVAL '1week' "
                               f"ORDER BY appointment_time asc")
                week_time = cursor.fetchall()
                for date in week_time:
                    date_btn = types.KeyboardButton(f"{date[0].strftime('%d-%m-%Y, %H:%M')}")
                    week_schedule_buttons.append(date[0].strftime('%d-%m-%Y, %H:%M'))
                    week_markup.add(date_btn)
            except Exception as ex:
                print("Error fetching dates", ex)

        bot.send_message(message.chat.id, "Выберите подходящую дату", reply_markup=week_markup)
    # ///////////////////////////////////////ЗАПИСЬ НА СВОБОДНОЕ ВРЕМЯ НА НЕДЕЛЕ////////////////////////////////////////
    if message.text in week_schedule_buttons:
        chosen_time = week_time[week_schedule_buttons.index(message.text)]
        markup_accept = types.ReplyKeyboardMarkup()
        yes = types.KeyboardButton("Да")
        no = types.KeyboardButton("Нет, выбрать другой вариант")
        markup_accept.add(yes, no)
        bot.send_message(message.chat.id, f"Вы хотите записаться на {message.text}?", reply_markup=markup_accept)

    if message.text == "Да":
        msg = bot.send_message(message.chat.id, "Как вас зовут?(Фамилия Имя)", reply_markup=None)
        bot.register_next_step_handler(msg, get_contacts)


# Запись имени в базу
def get_contacts(message):
    name = message.text.split()
    telegram_id = message.from_user.id
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                f"UPDATE {sql_mapping(chosen_doctor)} "
                f"SET patient_last_name = '{name[0]}', "
                f"patient_first_name = '{name[1]}', "
                f"doctor_busy = true ,"
                f"telegram_id = {telegram_id} "
                f"WHERE appointment_time = '{chosen_time[0]}'")
        except Exception as ex:
            print("Error inserting patient", ex)
        finally:
            bot.send_message(message.chat.id, "Имя принято")
            print("success")
    msg_phone = bot.send_message(message.chat.id, "Номер мобильного телефона?(+7XXXXXXXXXX)")
    bot.register_next_step_handler(msg_phone, get_phone_number)


def get_phone_number(message):
    global phone
    global new_appointment
    phone = message.text
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                f"UPDATE {sql_mapping(chosen_doctor)} "
                f"SET patient_phone = '{phone}' "
                f"WHERE appointment_time = '{chosen_time[0]}'")
        except Exception as ex:
            print("Error inserting patient", ex)
        finally:
            bot.send_message(message.chat.id,
                             "Телефон принят, вы успешно зарегистрировались. "
                             "Нажав на соответствующую кнопку, вы можете посмотреть или отменить свои записи")
            new_appointment = True
            start(message)
            print("success")


bot.polling(non_stop=True)
