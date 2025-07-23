from datetime import datetime
from pprint import pprint

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext
from config import API_KEY
import messages
import requests

from constants import week_days, months, contact_info, cities, users

BASE_URL = 'http://api.weatherapi.com/v1'


def start(update: Update, context: CallbackContext):
    user = update.effective_user

    users.append({
        'id': user.id,
        'full_name': user.full_name,
        'username': user.username,
        'city': None,
    })
    
    update.message.reply_html(
        messages.welcome_text.format(full_name=user.full_name)
    )
    select_category(update, context)


def select_category(update: Update, context: CallbackContext):
    """Sends a message with a list of categories to choose from."""
    update.message.reply_html(
        messages.select_category,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton('⛅️ Hozirgi ob-havo'), KeyboardButton('📍 Lokatsiya bo''yicha aniqlash', request_location=True)],
                [KeyboardButton('🕔 Soatlik ob-havo'), KeyboardButton('🗓 Haftalik ob-havo')],
                [KeyboardButton('📍 Hududni o\'zgartirish')],
                [KeyboardButton('📞 Aloqa')]
            ],
            resize_keyboard=True
        )
    )


def send_weather_by_location(update: Update, context: CallbackContext):
    location = update.message.location

    url = f"{BASE_URL}/current.json"
    payload = {
        'key': API_KEY,
        'q': f'{location.latitude},{location.longitude}'
    }
    response = requests.get(url, params=payload)

    data = response.json()

    pprint(data)

    now = datetime.now()

    update.message.reply_html(
        messages.current_weather.format(
            week_day=week_days[now.weekday() + 1],
            day=now.day,
            month=months[now.month],
            city=data['location']['region'],
            district=data['location']['name'],
            temp_c=data['current']['temp_c'],
            feelslike_c=data['current']['feelslike_c'],
            cloud=data['current']['cloud'],
            humidity=data['current']['humidity'],
            wind_mph=data['current']['wind_mph'],
            pressure_mb=data['current']['pressure_mb']
        )
    )
    

def send_contact(update: Update, context: CallbackContext):
    """Sends contact information to the user."""
    update.message.reply_html(
        contact_info["contact_info"]
    )


def send_current_weather(update: Update, context: CallbackContext):
    """Sends current weather information."""
    user = None

    for u in users:
        if u['id'] == update.effective_user.id:
            user = u
            break

    if user is None or user['city'] is None:
        update.message.reply_html(
            "Iltimos, avval hududni tanlang:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard= [[KeyboardButton(city['name'])] for city in cities] + [[KeyboardButton("Orqaga")]],
                resize_keyboard=True
            )
        )
        return
    
    url = f"{BASE_URL}/current.json"
    payload = {
        'key': API_KEY,
        'q': user['city']
    }
    response = requests.get(url, params=payload)
    data = response.json()
    now = datetime.now()
    update.message.reply_html(
        messages.current_weather.format(
            week_day=week_days[now.weekday() + 1],
            day=now.day,
            month=months[now.month],
            city=data['location']['region'],
            district=data['location']['name'],
            temp_c=data['current']['temp_c'],
            feelslike_c=data['current']['feelslike_c'],
            cloud=data['current']['cloud'],
            humidity=data['current']['humidity'],
            wind_mph=data['current']['wind_mph'],
            pressure_mb=data['current']['pressure_mb']
        )
    )


def send_hourly_weather(update: Update, context: CallbackContext):
    """Sends hourly weather information."""
    user = None

    for u in users:
        if u['id'] == update.effective_user.id:
            user = u
            break

    if user is None or user['city'] is None:
        update.message.reply_html(
            "Iltimos, avval hududni tanlang:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(city['name'])] for city in cities] + [[KeyboardButton("Orqaga")]],
                resize_keyboard=True
            )
        )
        return

    url = f"{BASE_URL}/forecast.json"
    payload = {
        'key': API_KEY,
        'q': user['city'],
        'hours': 12
    }
    response = requests.get(url, params=payload)
    data = response.json()

    hourly_data = data['forecast']['forecastday'][0]['hour']
    
    hourly_weather = "\n".join(
        f"{hour['time']}: {hour['temp_c']}°C, {hour['condition']['text']}" for hour in hourly_data
    )

    update.message.reply_html(f"12 soatlik ob-havo ma'lumotlari:\n{hourly_weather}")


def change_location(update: Update, context: CallbackContext):
    """Changes the location for weather updates."""
    # set user city to None
    i = 0

    while i < len(users):
        if users[i]['id'] == update.effective_user.id:
            users[i]['city'] = None
            break
        i += 1

    send_current_weather(update, context)


def send_weekly_weather(update: Update, context: CallbackContext):
    """Sends weekly weather information."""
    user = None
    for u in users:
        if u['id'] == update.effective_user.id:
            user = u
            break

    if user is None or user['city'] is None:
        update.message.reply_html(
            "Iltimos, avval hududni tanlang:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(city['name'])] for city in cities] + [[KeyboardButton("Orqaga")]],
                resize_keyboard=True
            )
        )
        return

    url = f"{BASE_URL}/forecast.json"
    payload = {
        'key': API_KEY,
        'q': user['city'],
        'days': 7
    }
    response = requests.get(url, params=payload)
    data = response.json()

    weekly_data = data['forecast']['forecastday']
    
    weekly_weather = "\n".join(
        f"{day['date']}: {day['day']['avgtemp_c']}°C, {day['day']['condition']['text']}" for day in weekly_data
    )

    update.message.reply_html(f"Haftalik ob-havo ma'lumotlari:\n{weekly_weather}")


def go_back(update: Update, context: CallbackContext):
    """Handles the 'go back' action."""
    select_category(update, context)


def handle_text(update: Update, context: CallbackContext):
    """Handles any text input from the user."""
    text = update.message.text

    if text in [city['name'] for city in cities]:

        i = 0
        while i < len(users):
            if users[i]['id'] == update.effective_user.id:
                users[i]['city'] = text
                break
            i += 1

        update.message.reply_html(f"Hudud o'zgartirildi: {text}")
        select_category(update, context)
    else:
        update.message.reply_html("Iltimos, tanlangan bo'limlardan birini tanlang.")
