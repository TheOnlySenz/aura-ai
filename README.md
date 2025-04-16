# Aura AI - Text-to-Speech Assistant

A powerful AI assistant that converts text to speech with customizable voices and parameters.

## Features

- Real-time text-to-speech conversion
- Voice customization options
- Adjustable speech speed and volume
- Modern API interface
- Support for multiple languages

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

The application will start on http://localhost:8000

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Example Usage

```python
import requests

url = "http://localhost:8000/tts"
data = {
    "text": "Hello, how can I assist you today?",
    "voice": "default",
    "speed": 1.0,
    "volume": 1.0
}

response = requests.post(url, json=data)
print(response.json())
```

## License

MIT License