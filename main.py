import pyttsx3
import argparse
import json
import os
from datetime import datetime
import webbrowser
import requests
from bs4 import BeautifulSoup
import subprocess
import platform
import re
import random
import math
import calendar
from dateutil import parser
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import phonenumbers
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import pickle
import uuid
import base64
import pytz
import pandas as pd
import yfinance as yf
import schedule
import time
from playsound import playsound
import vlc
from twilio.rest import Client
from geopy.geocoders import Nominatim
import pycountry
from langdetect import detect
from translate import Translator
from pyttsx3.drivers import sapi5

# Load environment variables
load_dotenv()

class AuraAI:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.current_voice = 0
        self.rate = 200
        self.volume = 1.0
        self.history = []
        self.commands = {
            "time": self.get_current_time,
            "weather": self.get_weather,
            "news": self.get_news,
            "joke": self.tell_joke,
            "calculate": self.calculate,
            "convert": self.convert_units,
            "remind": self.set_reminder,
            "calendar": self.show_calendar,
            "quote": self.get_quote,
            "search": self.search_web,
            "open": self.open_app,
            "list_voices": self.list_voices,
            "set_voice": self.set_voice,
            "set_rate": self.set_rate,
            "set_volume": self.set_volume,
            "history": self.show_history,
            "research": self.research_topic,
            "email": self.send_email,
            "text": self.send_text,
            "call": self.make_phone_call,
            "slack": self.send_slack_message,
            "todo": self.manage_todo,
            "event": self.manage_event,
            "currency": self.convert_currency,
            "stock": self.get_stock_info,
            "timer": self.set_timer,
            "alarm": self.set_alarm,
            "music": self.play_music,
            "timezone": self.get_timezone,
            "translate": self.translate_text,
            "define": self.define_word,
            "location": self.get_location,
            "country": self.get_country_info,
            "language": self.detect_language,
            "set_language": self.set_language
        }
        self.reminders = []
        self.todos = []
        self.scopes = ['https://www.googleapis.com/auth/calendar',
                      'https://www.googleapis.com/auth/gmail.send']
        self.credentials = None
        self.gmail_service = None
        self.calendar_service = None
        self.slack_client = None
        self.twilio_client = None
        self.setup_google_services()
        self.setup_slack()
        self.setup_twilio()
        self.scheduler = schedule.Scheduler()
        self.player = vlc.Instance()
        self.geolocator = Nominatim(user_agent="aura_ai")
        self.current_language = "en"
        self.supported_languages = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "hi": "Hindi",
            "ar": "Arabic"
        }

    def get_location(self, query):
        try:
            location = self.geolocator.geocode(query)
            if location:
                self.speak(f"Found location: {location.address}")
                return {
                    "address": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude
                }
            else:
                self.speak("Sorry, I couldn't find that location")
                return "Location not found"
        except Exception as e:
            self.speak("Sorry, I couldn't get the location information")
            return str(e)

    def get_country_info(self, country_name):
        try:
            country = pycountry.countries.get(name=country_name)
            if country:
                info = {
                    "name": country.name,
                    "alpha_2": country.alpha_2,
                    "alpha_3": country.alpha_3,
                    "numeric": country.numeric,
                    "official_name": getattr(country, "official_name", "")
                }
                self.speak(f"Country information for {country.name}")
                return info
            else:
                self.speak("Sorry, I couldn't find information about that country")
                return "Country not found"
        except Exception as e:
            self.speak("Sorry, I couldn't get the country information")
            return str(e)

    def detect_language(self, text):
        try:
            lang = detect(text)
            self.speak(f"Detected language: {self.supported_languages.get(lang, 'Unknown')}")
            return lang
        except Exception as e:
            self.speak("Sorry, I couldn't detect the language")
            return str(e)

    def set_language(self, language_code):
        try:
            if language_code in self.supported_languages:
                self.current_language = language_code
                # Update voice based on language
                self.set_voice_based_on_language(language_code)
                self.speak(f"Language set to {self.supported_languages[language_code]}")
                return self.current_language
            else:
                self.speak("Sorry, that language is not supported")
                return "Language not supported"
        except Exception as e:
            self.speak("Sorry, I couldn't set the language")
            return str(e)

    def set_voice_based_on_language(self, language_code):
        try:
            # Find a voice that matches the language
            for voice in self.voices:
                if language_code in voice.languages[0].lower():
                    self.engine.setProperty('voice', voice.id)
                    self.speak(f"Voice set for {self.supported_languages[language_code]}")
                    return True
            return False
        except Exception as e:
            self.speak("Sorry, I couldn't set the voice")
            return False

    def translate_text(self, text, target_language=None):
        try:
            if not target_language:
                target_language = self.current_language
            
            translator = Translator(to_lang=target_language)
            translation = translator.translate(text)
            self.speak(f"Translation: {translation}")
            return translation
        except Exception as e:
            self.speak("Sorry, I couldn't translate the text")
            return str(e)

    def get_timezone(self, location):
        try:
            # Get timezone information
            tz = pytz.timezone(location)
            now = datetime.now(tz)
            
            self.speak(f"The current time in {location} is {now.strftime('%I:%M %p')}")
            return {
                "location": location,
                "timezone": str(tz),
                "time": now.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            self.speak("Sorry, I couldn't get the timezone information")
            return str(e)

    def convert_currency(self, amount, from_currency, to_currency):
        try:
            # Convert currency codes to uppercase
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            # Get exchange rate
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                rate = data["rates"].get(to_currency)
                if rate:
                    result = float(amount) * rate
                    self.speak(f"{amount} {from_currency} is approximately {result:.2f} {to_currency}")
                    return result
                else:
                    self.speak(f"Currency {to_currency} not supported")
                    return "Currency not supported"
            else:
                self.speak("Sorry, I couldn't fetch the currency conversion rate")
                return "Conversion not available"
        except Exception as e:
            self.speak("Sorry, I couldn't perform the currency conversion")
            return str(e)

    def get_current_time(self, timezone=None):
        try:
            if timezone:
                tz = pytz.timezone(timezone)
                now = datetime.now(tz)
            else:
                now = datetime.now()
            
            current_time = now.strftime("%I:%M %p")
            if timezone:
                self.speak(f"The current time in {timezone} is {current_time}")
            else:
                self.speak(f"The current time is {current_time}")
            return current_time
        except Exception as e:
            self.speak("Sorry, I couldn't get the current time")
            return str(e)

    def process_command(self, command):
        # Detect language of the command
        try:
            lang = detect(command)
            if lang != self.current_language:
                self.set_language(lang)
        except:
            pass

        parts = command.split()
        if parts[0] in self.commands:
            func = self.commands[parts[0]]
            args = parts[1:] if len(parts) > 1 else []
            return func(*args)
        else:
            # Try to interpret as a natural language command
            if "weather" in command.lower():
                location = "".join(command.split()[1:]) if len(command.split()) > 1 else "current location"
                return self.get_weather(location)
            elif "time" in command.lower():
                timezone = "".join(command.split()[1:]) if len(command.split()) > 1 else None
                return self.get_current_time(timezone)
            elif "translate" in command.lower():
                text = "".join(command.split()[1:]) if len(command.split()) > 1 else ""
                return self.translate_text(text)
            else:
                self.speak(f"Unknown command: {parts[0]}")
                return f"Unknown command: {parts[0]}"

def main():
    parser = argparse.ArgumentParser(description='Aura AI - Global Assistant')
    parser.add_argument('command', nargs='*', help='Command to execute')
    args = parser.parse_args()
    
    aura = AuraAI()
    
    if args.command:
        command = ' '.join(args.command)
        result = aura.process_command(command)
        print(json.dumps(result, indent=2))
    else:
        print("Available commands:")
        print("- time [timezone]: Get current time")
        print("- weather [location]: Get weather information")
        print("- news [category]: Get news headlines")
        print("- joke: Get a random joke")
        print("- calculate [expression]: Perform calculations")
        print("- convert [value] [from_unit] [to_unit]: Convert units")
        print("- remind [text] [when]: Set a reminder")
        print("- calendar [month] [year]: Show calendar")
        print("- quote: Get a random quote")
        print("- search [query]: Search the web")
        print("- open [app_name]: Open an application")
        print("- list_voices: Show available voices")
        print("- set_voice [id]: Change voice")
        print("- set_rate [rate]: Set speaking rate")
        print("- set_volume [volume]: Set volume level")
        print("- history: Show command history")
        print("- research [topic]: Research a topic")
        print("- email [recipient] [subject] [body]: Send an email")
        print("- text [recipient] [message]: Send a text message")
        print("- call [recipient] [message]: Make a phone call")
        print("- slack [channel] [message]: Send a Slack message")
        print("- todo [action] [task] [priority]: Manage your todo list")
        print("- event [action] [details]: Manage your calendar events")
        print("- currency [amount] [from_currency] [to_currency]: Convert currencies")
        print("- stock [symbol]: Get stock market information")
        print("- timer [duration]: Set a timer")
        print("- alarm [time]: Set an alarm")
        print("- music [song_name]: Play music")
        print("- timezone [location]: Get timezone information")
        print("- translate [text] [language]: Translate text")
        print("- define [word]: Get word definition")
        print("- location [query]: Get location information")
        print("- country [name]: Get country information")
        print("- language [text]: Detect language")
        print("- set_language [code]: Set preferred language")

if __name__ == "__main__":
    from app import create_app
    from app.aura_ai import AuraAI

    app = create_app()
    app.run(debug=True, port=5000)
