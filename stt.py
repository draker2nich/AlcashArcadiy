#!/usr/bin/env python3
"""
Высокопроизводительный голосовой помощник с wake-word детекцией
Оптимизирован для работы на слабых ПК с минимальной задержкой
"""

import queue
import threading
import numpy as np
import sounddevice as sd
import vosk
import json
import sys
from collections import deque
from time import time

class VoiceAssistant:
    def __init__(self, model_path="vosk-model-small-ru-0.22", wake_word="привет ассистент"):
        # Инициализация модели Vosk (легковесная, работает оффлайн)
        self.model = vosk.Model(model_path)
        self.wake_word = wake_word.lower()
        
        # Параметры аудио (оптимизированы для баланса качество/производительность)
        self.sample_rate = 16000  # Оптимальная частота для распознавания
        self.block_size = 512     # Малый размер блока для быстрого отклика
        self.channels = 1
        
        # Очередь аудио с ограничением для предотвращения переполнения памяти
        self.audio_queue = queue.Queue(maxsize=100)
        
        # Буфер для детекции wake-word (3 секунды)
        self.wake_buffer = deque(maxlen=int(3 * self.sample_rate / self.block_size))
        self.is_listening = False
        
        # Распознаватели
        self.wake_rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
        self.main_rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
        
        # Оптимизация: отключаем логирование Vosk для производительности
        vosk.SetLogLevel(-1)
        
    def audio_callback(self, indata, frames, time_info, status):
        """Callback для захвата аудио (выполняется в отдельном потоке)"""
        if status:
            print(f"Ошибка аудио: {status}", file=sys.stderr)
        
        # Копируем данные в очередь без блокировки
        try:
            self.audio_queue.put_nowait(indata.copy())
        except queue.Full:
            pass  # Пропускаем кадр при переполнении
    
    def process_audio(self):
        """Основной цикл обработки аудио"""
        while True:
            try:
                # Получаем аудио с таймаутом для отзывчивости
                audio_chunk = self.audio_queue.get(timeout=0.1)
                
                # Конвертируем в bytes для Vosk
                audio_bytes = (audio_chunk * 32768).astype(np.int16).tobytes()
                
                if not self.is_listening:
                    # Режим ожидания wake-word
                    if self.wake_rec.AcceptWaveform(audio_bytes):
                        result = json.loads(self.wake_rec.Result())
                        text = result.get('text', '').lower()
                        
                        if self.wake_word in text:
                            self.is_listening = True
                            print("\n🎤 Слушаю...")
                            # Сброс основного распознавателя
                            self.main_rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
                else:
                    # Режим распознавания команды
                    if self.main_rec.AcceptWaveform(audio_bytes):
                        result = json.loads(self.main_rec.Result())
                        text = result.get('text', '').strip()
                        
                        if text:
                            print(f"📝 Распознано: {text}")
                            self.process_command(text)
                            self.is_listening = False
                            print("💤 Жду wake-word...")
                    else:
                        # Проверяем промежуточный результат для отзывчивости
                        partial = json.loads(self.main_rec.PartialResult())
                        if partial.get('partial'):
                            print(f"\r🔄 {partial['partial']}", end='', flush=True)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Ошибка обработки: {e}", file=sys.stderr)
    
    def process_command(self, text):
        """Обработка распознанной команды"""
        # Здесь добавьте логику обработки команд
        if "время" in text or "который час" in text:
            from datetime import datetime
            print(f"⏰ Сейчас {datetime.now().strftime('%H:%M')}")
        elif "стоп" in text or "выход" in text:
            print("👋 До свидания!")
            self.stop()
        else:
            print(f"❓ Команда не распознана: {text}")
    
    def start(self):
        """Запуск голосового помощника"""
        print(f"🚀 Голосовой помощник запущен")
        print(f"🔊 Wake-word: '{self.wake_word}'")
        print(f"💤 Жду wake-word...")
        
        # Запуск аудио потока
        with sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            channels=self.channels,
            callback=self.audio_callback,
            dtype=np.float32
        ):
            # Обработка в основном потоке
            self.process_audio()
    
    def stop(self):
        """Остановка помощника"""
        sys.exit(0)

# Быстрая инициализация и запуск
if __name__ == "__main__":
    try:
        # Создаем и запускаем помощника
        assistant = VoiceAssistant(
            model_path="vosk-model-small-ru-0.22",  # Используйте small модель для скорости
            wake_word="аркаша"  # Можно изменить на любое слово
        )
        assistant.start()
        
    except KeyboardInterrupt:
        print("\n👋 Остановлено пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)