import requests
import json
import random
from .personality import ArkadyPersonality

class ArkadyAI:
    def __init__(self, model_name="llama3.2:1b", ollama_url="http://localhost:11434", swear_intensity='medium'):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.personality = ArkadyPersonality(swear_intensity=swear_intensity)
        self.conversation_history = []
        self.max_history = 5  # Храним последние 5 сообщений
        
        # Проверяем соединение
        self.check_ollama_connection()
    
    def check_ollama_connection(self):
        """Проверяет подключение к Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/version", timeout=5)
            if response.status_code == 200:
                print("✓ Подключение к Ollama установлено")
                
                # Проверяем наличие модели
                models_response = requests.get(f"{self.ollama_url}/api/tags")
                if models_response.status_code == 200:
                    models = models_response.json().get('models', [])
                    model_names = [m['name'] for m in models]
                    
                    if self.model_name in model_names:
                        print(f"✓ Модель {self.model_name} найдена")
                    else:
                        print(f"⚠️  Модель {self.model_name} не найдена")
                        print(f"Доступные модели: {model_names}")
                        
                        # Используем первую доступную модель
                        if model_names:
                            self.model_name = model_names[0]
                            print(f"Использую модель: {self.model_name}")
                        else:
                            raise Exception("Нет доступных моделей в Ollama")
                            
            else:
                raise Exception(f"Ollama не отвечает: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Ошибка подключения к Ollama: {e}")
            print("Убедитесь что Ollama запущен: ollama serve")
            raise
    
    def generate_response(self, user_input):
        """Генерирует ответ в стиле Аркадия"""
        try:
            # Подготавливаем промпт
            prompt = self._build_prompt(user_input)
            
            # Запрос к Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,  # Добавляем вариативности
                        "top_p": 0.9,
                        "num_predict": 100,  # Ограничиваем длину ответа
                        "stop": ["\n\n", "Пользователь:", "User:"]
                    }
                },
                timeout=60  # Увеличиваем таймаут до 60 секунд
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                
                if ai_response:
                    # Обрабатываем ответ через личность
                    processed_response = self.personality.process_response(ai_response)
                    
                    # Добавляем в историю
                    self._add_to_history(user_input, processed_response)
                    
                    return processed_response
                else:
                    return self._get_fallback_response()
                    
            else:
                print(f"Ошибка Ollama API: {response.status_code}")
                return self._get_fallback_response()
                
        except Exception as e:
            print(f"Ошибка генерации ответа: {e}")
            return self._get_fallback_response()
    
    def _build_prompt(self, user_input):
        """Строит промпт для ИИ"""
        # Базовый системный промпт
        prompt = self.personality.system_prompt + "\n\n"
        
        # Добавляем контекст из истории
        if self.conversation_history:
            prompt += "Предыдущий разговор:\n"
            for entry in self.conversation_history[-3:]:  # Последние 3 обмена
                prompt += f"Пользователь: {entry['user']}\n"
                prompt += f"Аркадий: {entry['bot']}\n"
            prompt += "\n"
        
        # Текущий вопрос
        prompt += f"Пользователь: {user_input}\n"
        prompt += "Аркадий:"
        
        return prompt
    
    def _add_to_history(self, user_input, bot_response):
        """Добавляет обмен в историю"""
        self.conversation_history.append({
            'user': user_input,
            'bot': bot_response
        })
        
        # Ограничиваем размер истории
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def _get_fallback_response(self):
        """Резервные ответы если ИИ не работает"""
        fallback_responses = [
            "Ну вот, не работает у меня башка сегодня, браток",
            "Слушай, что-то я туплю сейчас",
            "Давай по-другому спроси, а то не врубаюсь",
            "Хм, не понял я тебя, дорогуша",
            "Короче, не допер я, повтори",
            "Что-то мозги не варят, скажи еще раз"
        ]
        return random.choice(fallback_responses)
    
    def get_greeting(self):
        """Приветствие при запуске"""
        return self.personality.get_greeting()
    
    def handle_special_commands(self, user_input):
        """Обрабатывает специальные команды"""
        input_lower = user_input.lower().strip()
        
        # Команды выхода
        if any(word in input_lower for word in ['пока', 'выход', 'стоп', 'хватит', 'всё']):
            farewell_responses = [
                "Ну давай, браток, удачи тебе",
                "Пока-пока, дорогуша",
                "До встречи, корешок",
                "Ладно, бывай",
                "Увидимся еще, мужик"
            ]
            return random.choice(farewell_responses), True
        
        # Команды справки
        if any(word in input_lower for word in ['помощь', 'справка', 'что умеешь']):
            help_response = "Ну я Аркадий, короче. Говори что надо - отвечу как смогу, браток. Чтобы выйти - скажи 'пока'."
            return help_response, False
        
        return None, False
    
    def clear_history(self):
        """Очищает историю разговора"""
        self.conversation_history = []
        print("История разговора очищена")