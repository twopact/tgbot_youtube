import os
import telebot
from telebot import types
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver


chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
options = chrome_options
driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com")

token = "6132324027:AAHWbW7neboOBD130vLM1P_-1bBY3ld5AH4"
bot = telebot.TeleBot(token)

# Создаем объект для клавиатуры и добавляем кнопки
keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

# Создаем объекты для кнопок и добавляем их на клавиатуру
videos_button = types.KeyboardButton('Искать видео')
channel_button = types.KeyboardButton('Искать канал')
keyboard.add(videos_button, channel_button)

# Обрабатываем команду start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Нажми на кнопку для дальнейших действий.", reply_markup=keyboard)

# Обрабатываем нажатие на кнопку "Искать видео"
@bot.message_handler(func=lambda message: message.text == 'Искать видео')
def search_videos(message):
    message = bot.send_message(message.chat.id, "Введите текст, который вы хотите найти в YouTube")
    bot.register_next_step_handler(message, search)

# Обрабатываем нажатие на кнопку "Искать канал"
@bot.message_handler(func=lambda message: message.text == 'Искать канал')
def search_channel(message):
    message = bot.send_message(message.chat.id, 'Введите id YouTube-канала, на котором вы хотите найти видео, например, "MrBeast" или "user-zn5cc1xv8x"')
    bot.register_next_step_handler(message, search_from_channel)

# Функция для поиска видео по запросу пользователя
def search(message):
    bot.send_message(message.chat.id, "Вы выбрали \"Искать видео\". \nПожалуйста, подождите, начинаю поиск...")
    video_href = "https://www.youtube.com/results?search_query=" + message.text
    driver.get(video_href)
    sleep(3)
    videos = driver.find_elements(By.ID, "video-title")
    num_videos = len(videos)
    if num_videos == 0:
        bot.send_message(message.chat.id, "Ничего не найдено, напишите другой текст")
        return
    bot.send_message(message.chat.id, f"Найдено {num_videos} видео. Сколько из них вы хотите получить?")
    bot.register_next_step_handler(message, send_videos, videos)


# Функция для поиска видео на канале
def search_from_channel(message):
    bot.send_message(message.chat.id, "Вы выбрали \"Искать канал\", пожалуйста, подождите, начинаю поиск...")
    driver.get("https://www.youtube.com/@" + message.text + "/videos")
    sleep(3)
    videos = driver.find_elements(By.ID, "thumbnail")
    num_videos = len(videos)
    if num_videos == 0:
        bot.send_message(message.chat.id, "Такой канал не найден, введите другой")
        return
    bot.send_message(message.chat.id, f"Найдено {num_videos} видео. Сколько из них вы хотите получить?")
    bot.register_next_step_handler(message, send_channel_videos, videos)


# Функция для отправки запрошенного количества видео
def send_videos(message, videos):
    count = int(message.text)
    if count > len(videos):
        bot.send_message(message.chat.id, f"Количество запрошенных видео ({count}) больше, чем количество найденных ({len(videos)}).")
        return
    bot.send_message(message.chat.id, f"Отправляю {count} видео...")
    for i in range(count):
        bot.send_message(message.chat.id, videos[i].get_attribute('href'))


# Функция для отправки запрошенного количества видео на канале
def send_channel_videos(message, videos):
    # Получаем запрошенное количество видео из сообщения и приводим его к типу int
    count = int(message.text)
    # Если запрошенное количество видео больше, чем количество найденных, то отправляем сообщение с ошибкой и прекращаем выполнение функции
    if count > len(videos):
        bot.send_message(message.chat.id, f"Количество запрошенных видео ({count}) больше, чем количество найденных ({len(videos)}).")
        return
    # Отправляем сообщение о том, что начинаем отправлять видео
    bot.send_message(message.chat.id, f"Отправляю {count} видео...")
    # Отправляем запрошенное количество видео
    for i in range(count):
        # Находим элементы с видео на странице и отправляем ссылку на i-тое видео
        bot.send_message(message.chat.id, driver.find_elements(By.ID, "dismissible")[i].find_element(By.ID, "thumbnail").get_attribute("href"))


print('#Bot started')
bot.polling(none_stop=True, interval=0)