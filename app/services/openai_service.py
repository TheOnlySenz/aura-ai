import os
import openai
from dotenv import load_dotenv
from typing import Dict, List, Optional
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

class OpenAIService:
    def __init__(self):
        self.model = "gpt-4"
        self.temperature = 0.7
        self.max_tokens = 2000
        self.system_prompt = """
You are Aura, an AI assistant designed to help users with various tasks.
You can understand and respond to natural language commands.
You can perform tasks like:
- Answering questions
- Writing code
- Providing explanations
- Generating content
- Analyzing data
- Making recommendations
- Managing files and directories
- Web browsing and search
- System monitoring
- Calendar and scheduling
- Music and media control
- Weather and location services
- Translation and language support
- Email and messaging
- Social media integration
- System automation
- Code generation and debugging
- Mathematical calculations
- Unit conversions
- Time zone management
- News and information retrieval
- Image generation and analysis
- Voice command processing
- Multi-language support
- Context-aware responses
- Personalized recommendations
- Task automation
- Integration with external services

You should:
- Be concise and clear in your responses
- Provide accurate and helpful information
- Use markdown formatting when appropriate
- Include code examples when relevant
- Be conversational but professional
- Never make things up
- Always stay within your capabilities
- Maintain user privacy and security
- Handle errors gracefully
- Provide context-aware responses
- Support natural language processing
- Maintain state between conversations
- Handle multiple tasks simultaneously
"""

    def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None):
        try:
            if not model:
                model = self.model
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_response(self, user_input: str, conversation_history: List[Dict[str, str]] = None):
        if not conversation_history:
            conversation_history = []
            
        # Add system prompt
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        # Get response from OpenAI
        response = self.chat_completion(messages)
        
        # Add response to history
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})
        
        return {
            "response": response,
            "conversation_history": conversation_history
        }

    def code_completion(self, prompt: str, language: str = "python") -> str:
        messages = [
            {"role": "system", "content": f"You are a code assistant. Generate code in {language} language."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages)

    def content_generation(self, prompt: str, style: str = "professional") -> str:
        messages = [
            {"role": "system", "content": f"You are a content writer. Generate content in {style} style."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages)

    def analyze_text(self, text: str, analysis_type: str = "sentiment") -> Dict:
        messages = [
            {"role": "system", "content": "You are a text analyzer. Analyze the given text."},
            {"role": "user", "content": f"Analyze this text: {text}\nType of analysis: {analysis_type}"}
        ]
        
        response = self.chat_completion(messages)
        try:
            return json.loads(response)
        except:
            return {"analysis": response}

    def summarize_text(self, text: str, length: str = "short") -> str:
        messages = [
            {"role": "system", "content": "You are a text summarizer. Generate a summary of the given text."},
            {"role": "user", "content": f"Summarize this text: {text}\nLength: {length}"}
        ]
        
        return self.chat_completion(messages)

    def generate_image(self, prompt: str) -> str:
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
        except Exception as e:
            return f"Error generating image: {str(e)}"

    def web_search(self, query: str) -> str:
        try:
            # Use OpenAI's Web Search API
            response = openai.Web.search(
                query=query,
                count=5
            )
            
            # Format results
            results = []
            for item in response:
                results.append(f"- {item['title']}: {item['snippet']}\n  URL: {item['url']}")
            
            return "\n".join(results)
        except Exception as e:
            return f"Error searching web: {str(e)}"

    def get_weather(self, location: str) -> str:
        try:
            # Use OpenAI's Weather API
            response = openai.Weather.current(
                location=location
            )
            
            return f"Current weather in {location}:\n" \
                   f"Temperature: {response['temperature']}°C\n" \
                   f"Condition: {response['condition']}\n" \
                   f"Humidity: {response['humidity']}%\n" \
                   f"Wind: {response['wind_speed']} km/h"
        except Exception as e:
            return f"Error getting weather: {str(e)}"

    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            response = openai.Translation.translate(
                text=text,
                source_language=source_lang,
                target_language=target_lang
            )
            return response['translated_text']
        except Exception as e:
            return f"Error translating text: {str(e)}"

    def code_debugger(self, code: str, language: str) -> str:
        messages = [
            {"role": "system", "content": f"You are a code debugger for {language}. Analyze the code and provide suggestions for improvements."},
            {"role": "user", "content": f"Please debug this {language} code:\n{code}"}
        ]
        
        return self.chat_completion(messages)

    def file_operations(self, operation: str, path: str) -> str:
        try:
            # Use OpenAI's File Operations API
            response = openai.File.operate(
                operation=operation,
                path=path
            )
            return response['result']
        except Exception as e:
            return f"Error performing file operation: {str(e)}"

    def system_monitor(self) -> Dict:
        try:
            # Use OpenAI's System Monitoring API
            response = openai.System.monitor()
            return {
                'cpu_usage': response['cpu_usage'],
                'memory_usage': response['memory_usage'],
                'disk_usage': response['disk_usage'],
                'network_usage': response['network_usage']
            }
        except Exception as e:
            return {"error": f"Error monitoring system: {str(e)}"}

    def schedule_event(self, event: str, time: str) -> str:
        try:
            # Use OpenAI's Calendar API
            response = openai.Calendar.schedule(
                event=event,
                time=time
            )
            return f"Event scheduled successfully: {response['event_id']}"
        except Exception as e:
            return f"Error scheduling event: {str(e)}"

    def get_news(self, category: str = "general") -> str:
        try:
            # Use OpenAI's News API
            response = openai.News.get(
                category=category,
                count=5
            )
            
            # Format results
            results = []
            for item in response:
                results.append(f"- {item['title']}: {item['summary']}\n  Source: {item['source']}\n  URL: {item['url']}")
            
            return "\n".join(results)
        except Exception as e:
            return f"Error getting news: {str(e)}"

    def analyze_code(self, code: str, language: str) -> str:
        messages = [
            {"role": "system", "content": f"You are a code analyzer for {language}. Analyze the code and provide detailed insights."},
            {"role": "user", "content": f"Please analyze this {language} code:\n{code}"}
        ]
        
        return self.chat_completion(messages)

    def generate_documentation(self, code: str, language: str) -> str:
        messages = [
            {"role": "system", "content": f"You are a documentation generator for {language}. Generate clear and concise documentation for the code."},
            {"role": "user", "content": f"Please generate documentation for this {language} code:\n{code}"}
        ]
        
        return self.chat_completion(messages)

    def optimize_code(self, code: str, language: str) -> str:
        messages = [
            {"role": "system", "content": f"You are a code optimizer for {language}. Analyze the code and provide optimized version with explanations."},
            {"role": "user", "content": f"Please optimize this {language} code:\n{code}"}
        ]
        
        return self.chat_completion(messages)

    def generate_test_cases(self, code: str, language: str) -> str:
        messages = [
            {"role": "system", "content": f"You are a test case generator for {language}. Generate comprehensive test cases for the code."},
            {"role": "user", "content": f"Please generate test cases for this {language} code:\n{code}"}
        ]
        
        return self.chat_completion(messages)

    def convert_code(self, code: str, from_lang: str, to_lang: str) -> str:
        messages = [
            {"role": "system", "content": f"You are a code converter. Convert code from {from_lang} to {to_lang}."},
            {"role": "user", "content": f"Please convert this {from_lang} code to {to_lang}:\n{code}"}
        ]
        
        return self.chat_completion(messages)

# Create a singleton instance
def get_openai_service():
    return OpenAIService()
