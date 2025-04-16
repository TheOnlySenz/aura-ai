from flask import Flask, render_template, jsonify, request
import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import random
import json
import os
from dotenv import load_dotenv
from app.services.openai_service import get_openai_service

app = Flask(__name__)

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

# Set up voice properties
tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 1.0)

# Initialize speech recognition
recognizer = sr.Recognizer()

# Initialize OpenAI service
openai_service = get_openai_service()

# Demo commands and responses
demo_commands = {
    'time': 'The current time is {time}',
    'date': 'Today is {date}',
    'weather': 'The weather is currently {weather}',
    'joke': 'Why don\'t scientists trust atoms? Because they make up everything!',
    'news': 'The latest news headline is {headline}',
    'search': 'Searching for {query}...',
    'reminder': 'Reminder set for {time} with message: {message}',
    'email': 'Email sent to {recipient} with subject: {subject}',
    'translate': '{text} in {language} is {translation}',
    'music': 'Playing music for {artist}',
    'volume': 'Volume set to {level}%',
    'rate': 'Speaking rate set to {speed} words per minute'
}

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

@app.route('/')
def index():
    return render_template('demo.html')

@app.route('/api/command', methods=['POST'])
def process_command():
    data = request.get_json()
    command = data.get('command', '').lower()
    
    # Check for wake word
    if not command.startswith('aura'):
        return jsonify({
            'status': 'error',
            'message': 'Please start with "Aura"'
        })
        
    # Remove wake word
    command = command.replace('aura', '').strip()
    
    # Process command
    response = process_voice_command(command)
    
    # If the response is a dictionary, convert it to JSON
    if isinstance(response, dict):
        response = json.dumps(response)
    
    return jsonify({
        'status': 'success',
        'result': response
    })

def process_voice_command(command):
    # Split command into parts
    parts = command.split()
    
    if not parts:
        return "Please provide a command"
        
    command_type = parts[0]
    
    # Handle different types of commands
    if command_type == 'time':
        now = datetime.datetime.now()
        return demo_commands['time'].format(time=now.strftime('%I:%M %p'))
    elif command_type == 'date':
        now = datetime.datetime.now()
        return demo_commands['date'].format(date=now.strftime('%A, %B %d, %Y'))
    elif command_type == 'weather':
        return demo_commands['weather'].format(weather='sunny')
    elif command_type == 'joke':
        return demo_commands['joke']
    elif command_type == 'news':
        return demo_commands['news'].format(headline='AI technology advances')
    elif command_type == 'search':
        query = ' '.join(parts[1:])
        return demo_commands['search'].format(query=query)
    elif command_type == 'reminder':
        if len(parts) >= 2:
            time = parts[1]
            message = ' '.join(parts[2:])
            return demo_commands['reminder'].format(time=time, message=message)
    elif command_type == 'email':
        if len(parts) >= 3:
            recipient = parts[1]
            subject = parts[2]
            body = ' '.join(parts[3:])
            return demo_commands['email'].format(recipient=recipient, subject=subject)
    elif command_type == 'translate':
        if len(parts) >= 2:
            language = parts[1]
            text = ' '.join(parts[2:])
            return demo_commands['translate'].format(
                text=text,
                language=language,
                translation=text  # In demo, just return the same text
            )
    elif command_type == 'music':
        if parts[1:]:
            artist = ' '.join(parts[1:])
            return demo_commands['music'].format(artist=artist)
    elif command_type == 'volume':
        if len(parts) > 1:
            level = int(parts[1])
            return demo_commands['volume'].format(level=level)
    elif command_type == 'rate':
        if len(parts) > 1:
            speed = int(parts[1])
            return demo_commands['rate'].format(speed=speed)
    elif command_type == 'help':
        return "I can help with many tasks! Try these commands:\n\n" + \
               "Aura time\nAura weather\nAura joke\nAura search python programming\n" + \
               "Aura code explain this code\nAura write python code to\n" + \
               "Aura summarize this article\nAura analyze this text\n" + \
               "Aura generate image of\nAura translate french hello\n" + \
               "Aura music classic rock\nAura volume 70\nAura rate 180"
    elif command_type == 'code':
        if len(parts) > 1:
            query = ' '.join(parts[1:])
            return openai_service.code_completion(query)
    elif command_type == 'write':
        if len(parts) > 1:
            query = ' '.join(parts[1:])
            return openai_service.content_generation(query)
    elif command_type == 'summarize':
        if len(parts) > 1:
            text = ' '.join(parts[1:])
            return openai_service.summarize_text(text)
    elif command_type == 'analyze':
        if len(parts) > 1:
            text = ' '.join(parts[1:])
            return openai_service.analyze_text(text)
    elif command_type == 'image':
        if len(parts) > 1:
            prompt = ' '.join(parts[1:])
            return openai_service.generate_image(prompt)
    
    return "I'm sorry, I don't understand that command. Try 'Aura help' for available commands."

@app.route('/api/voices')
def get_voices():
    voices = []
    for voice in tts_engine.getProperty('voices'):
        voices.append({
            'id': voice.id,
            'name': voice.name,
            'language': voice.languages[0]
        })
    return jsonify({
        'status': 'success',
        'voices': voices
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
