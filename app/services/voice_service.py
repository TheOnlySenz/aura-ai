import speech_recognition as sr
import pyttsx3
import numpy as np
import sounddevice as sd
import webrtcvad
import threading
import queue
import json
import os
from app.services.email_service import get_email_service
from app.services.calendar_service import get_calendar_service

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.vad = webrtcvad.Vad()
        self.voice_queue = queue.Queue()
        self.is_listening = False
        self.command_handlers = {
            'time': self.handle_time,
            'date': self.handle_date,
            'weather': self.handle_weather,
            'email': self.handle_email,
            'reminder': self.handle_reminder,
            'search': self.handle_search,
            'translate': self.handle_translate,
            'news': self.handle_news,
            'joke': self.handle_joke,
            'music': self.handle_music,
            'system': self.handle_system
        }
        
        # Set up voice properties
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        
        # Set up VAD parameters
        self.vad.set_mode(1)  # Normal sensitivity
        
    def start_listening(self):
        self.is_listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()
        
    def stop_listening(self):
        self.is_listening = False
        
    def _listen_loop(self):
        with sr.Microphone() as source:
            while self.is_listening:
                try:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source)
                    
                    # Listen for speech
                    audio = self.recognizer.listen(source, timeout=5)
                    
                    # Convert audio to text
                    command = self.recognizer.recognize_google(audio)
                    
                    # Process command
                    self.process_command(command)
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.speak("Sorry, I didn't understand that.")
                except sr.RequestError:
                    self.speak("Sorry, my speech service is down.")
                except Exception as e:
                    self.speak("An error occurred: " + str(e))
                    
    def process_command(self, command: str):
        # Convert command to lowercase and remove spaces
        command = command.lower().strip()
        
        # Check for wake word
        if not command.startswith('aura'):
            return
            
        # Remove wake word
        command = command.replace('aura', '').strip()
        
        # Split command into parts
        parts = command.split()
        
        if not parts:
            return
            
        # Get command type
        command_type = parts[0]
        
        # Get handler and arguments
        handler = self.command_handlers.get(command_type)
        if handler:
            try:
                handler(parts[1:])
            except Exception as e:
                self.speak("Error processing command: " + str(e))
        else:
            self.speak("I'm sorry, I don't understand that command.")
            
    def speak(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
        
    def handle_time(self, args):
        import datetime
        now = datetime.datetime.now()
        self.speak(f"The current time is {now.strftime('%I:%M %p')}")
        
    def handle_date(self, args):
        import datetime
        now = datetime.datetime.now()
        self.speak(f"Today is {now.strftime('%A, %B %d, %Y')}")
        
    def handle_weather(self, args):
        # Add weather API integration here
        self.speak("Weather functionality coming soon!")
        
    def handle_email(self, args):
        if len(args) >= 3:  # email [recipient] [subject] [body]
            recipient = args[0]
            subject = args[1]
            body = ' '.join(args[2:])
            
            email_service = get_email_service()
            result = email_service.send_email(
                to_email=recipient,
                subject=subject,
                body=body
            )
            
            if result['status'] == 'success':
                self.speak("Email sent successfully!")
            else:
                self.speak("Failed to send email.")
        else:
            self.speak("Please provide recipient, subject, and body for the email.")
            
    def handle_reminder(self, args):
        if len(args) >= 2:  # reminder [time] [message]
            time = args[0]
            message = ' '.join(args[1:])
            
            calendar_service = get_calendar_service()
            result = calendar_service.create_event(
                summary=message,
                start_time=time,
                end_time=time
            )
            
            if result['status'] == 'success':
                self.speak("Reminder set successfully!")
            else:
                self.speak("Failed to set reminder.")
        else:
            self.speak("Please provide time and message for the reminder.")
            
    def handle_search(self, args):
        query = ' '.join(args)
        # Add web search functionality here
        self.speak(f"Searching for {query}...")
        
    def handle_translate(self, args):
        if len(args) >= 2:  # translate [language] [text]
            target_lang = args[0]
            text = ' '.join(args[1:])
            # Add translation functionality here
            self.speak(f"Translation to {target_lang}: {text}")
        else:
            self.speak("Please provide target language and text to translate.")
            
    def handle_news(self, args):
        # Add news API integration here
        self.speak("Fetching latest news...")
        
    def handle_joke(self, args):
        # Add joke functionality here
        self.speak("Why don't scientists trust atoms? Because they make up everything!")
        
    def handle_music(self, args):
        if args:  # music [song/artist]
            query = ' '.join(args)
            # Add music playback functionality here
            self.speak(f"Playing music for {query}...")
        else:
            self.speak("Please provide a song or artist name.")
            
    def handle_system(self, args):
        if args:
            command = args[0]
            if command == 'volume':
                if len(args) > 1:
                    level = int(args[1])
                    self.engine.setProperty('volume', level/100)
                    self.speak(f"Volume set to {level}%")
            elif command == 'rate':
                if len(args) > 1:
                    speed = int(args[1])
                    self.engine.setProperty('rate', speed)
                    self.speak(f"Speaking rate set to {speed} words per minute")
            else:
                self.speak("Unknown system command.")
        else:
            self.speak("Please provide a system command.")
            
    def handle_error(self, error):
        self.speak("An error occurred: " + str(error))
