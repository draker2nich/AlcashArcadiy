#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import signal
from arkady.speech_recognition import SpeechRecognizer
from arkady.speech_synthesis import HoboVoiceSynthesizer
from arkady.text_generation import ArkadyAI

class ArkadyBot:
    def __init__(self, swear_level='medium'):
        self.running = False
        self.speech_recognizer = None
        self.voice_synthesizer = None
        self.ai_brain = None
        self.swear_level = swear_level
        
        # Обработка Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Обработка сигнала завершения"""
        print("\nЗавершение работы...")
        self.shutdown()
        sys.exit(0)
    
    def initialize(self):
        """Инициализация всех компонентов"""
        print("🤖 Запуск Аркадия...")
        print("=" * 50)
        
        try:
            # 1. Инициализация ИИ
            print("1️⃣  Подключение к мозгам...")
            self.ai_brain = ArkadyAI(swear_intensity=self.swear_level)
            
            # 2. Инициализация синтеза речи
            print("2️⃣  Настройка русского голоса...")
            self.voice_synthesizer = HoboVoiceSynthesizer()
            
            # 3. Инициализация распознавания речи
            print("3️⃣  Настройка слуха...")
            self.speech_recognizer = SpeechRecognizer()
            
            print("=" * 50)
            print("✅ Аркадий готов к работе!")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    def test_components(self):
        """Тест всех компонентов"""
        print("\n🧪 Тестирование компонентов...")
        
        # Тест голоса
        print("Тест голоса...")
        greeting = self.ai_brain.get_greeting()
        self.voice_synthesizer.speak_sync(greeting)
        
        input("Нажмите Enter чтобы продолжить...")
        return True
    
    def run(self):
        """Основной цикл работы бота"""
        if not self.initialize():
            return
        
        # Опциональный тест
        user_choice = input("Протестировать компоненты? (y/n): ").lower()
        if user_choice in ['y', 'yes', 'да', 'д']:
            if not self.test_components():
                return
        
        # Запуск основного цикла
        self.running = True
        self.main_loop()
    
    def main_loop(self):
        """Главный цикл взаимодействия"""
        print("\n" + "=" * 50)
        print("🎤 Аркадий слушает...")
        print("Скажите 'Аркадий' чтобы активировать")
        print("Для выхода скажите 'пока' или нажмите Ctrl+C")
        print("=" * 50)
        
        # Приветствие
        greeting = self.ai_brain.get_greeting()
        self.voice_synthesizer.speak(greeting)
        
        # Запуск прослушивания
        self.speech_recognizer.start_listening()
        
        try:
            while self.running:
                # Ждем активационное слово и команду
                user_command = self.speech_recognizer.wait_for_wake_word(timeout=30)
                
                if user_command:
                    print(f"👤 Пользователь: {user_command}")
                    
                    # Проверяем специальные команды
                    special_response, should_exit = self.ai_brain.handle_special_commands(user_command)
                    
                    if special_response:
                        self.voice_synthesizer.speak(special_response)
                        
                        if should_exit:
                            print("👋 До свидания!")
                            break
                    else:
                        # Генерируем обычный ответ
                        response = self.ai_brain.generate_response(user_command)
                        self.voice_synthesizer.speak(response)
                
                else:
                    # Таймаут - напоминаем о себе
                    if self.running:  # Проверяем что не завершаемся
                        reminders = [
                            "Я тут, браток",
                            "Слушаю тебя, дорогуша", 
                            "Говори, не стесняйся",
                            "Че молчишь?"
                        ]
                        import random
                        reminder = random.choice(reminders)
                        self.voice_synthesizer.speak(reminder)
                
                # Небольшая пауза между циклами
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nПрерывание пользователем")
        except Exception as e:
            print(f"Ошибка в главном цикле: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Корректное завершение работы"""
        print("🔄 Завершение работы...")
        
        self.running = False
        
        if self.speech_recognizer:
            self.speech_recognizer.cleanup()
        
        if self.voice_synthesizer:
            self.voice_synthesizer.cleanup()
        
        print("✅ Аркадий отключен")

def main():
    """Точка входа"""
    print("🚀 Запуск голосового помощника 'Аркадий'")
    print("Версия: 2.0 (Русский Бомжара Edition)")
    print()
    
    # Выбор уровня матов
    print("Выберите уровень мата:")
    print("1. Легкий (хрен, черт, дерьмо)")
    print("2. Средний (базовый набор)")
    print("3. Жесткий (все маты)")
    
    while True:
        choice = input("Введите номер (1-3) или Enter для среднего: ").strip()
        
        if choice == '1':
            swear_level = 'light'
            break
        elif choice == '2' or choice == '':
            swear_level = 'medium'
            break
        elif choice == '3':
            swear_level = 'hardcore'
            break
        else:
            print("Неверный выбор, попробуйте еще раз")
    
    print(f"Настройки: Русский TTS, Маты={swear_level}")
    
    bot = ArkadyBot(swear_level=swear_level)
    bot.run()

if __name__ == "__main__":
    main()