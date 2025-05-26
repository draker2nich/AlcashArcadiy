import json
import pyaudio
import vosk
import threading
import queue
import time

class SpeechRecognizer:
    def __init__(self, model_path="models/vosk-model-small-ru-0.22"):
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.microphone = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.wake_words = ["аркадий", "аркаша", "арк"]
        
        # Настройки аудио
        self.RATE = 16000
        self.CHUNK = 8000
        self.CHANNELS = 1
        
        self.setup_vosk()
        self.setup_microphone()
    
    def setup_vosk(self):
        """Инициализация Vosk"""
        try:
            print(f"Загружаем модель из {self.model_path}...")
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.RATE)
            print("✓ Vosk модель загружена")
        except Exception as e:
            print(f"✗ Ошибка загрузки Vosk: {e}")
            raise
    
    def setup_microphone(self):
        """Настройка микрофона"""
        try:
            self.microphone = pyaudio.PyAudio()
            print("✓ Микрофон готов")
        except Exception as e:
            print(f"✗ Ошибка микрофона: {e}")
            raise
    
    def start_listening(self):
        """Запуск прослушивания в отдельном потоке"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        print("🎤 Начинаю слушать...")
    
    def stop_listening(self):
        """Остановка прослушивания"""
        self.is_listening = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join(timeout=1)
        print("🔇 Прекратил слушать")
    
    def _listen_loop(self):
        """Основной цикл прослушивания"""
        stream = self.microphone.open(
            format=pyaudio.paInt16,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        print("Говорите 'Аркадий' чтобы активировать...")
        
        try:
            while self.is_listening:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').lower().strip()
                    
                    if text:
                        print(f"Услышал: {text}")
                        self.audio_queue.put(text)
                
                time.sleep(0.01)  # Небольшая пауза
                
        except Exception as e:
            print(f"Ошибка в цикле прослушивания: {e}")
        finally:
            stream.stop_stream()
            stream.close()
    
    def wait_for_wake_word(self, timeout=None):
        """Ждет ключевое слово активации"""
        start_time = time.time()
        
        while True:
            if timeout and (time.time() - start_time) > timeout:
                return None
            
            try:
                text = self.audio_queue.get(timeout=1)
                
                # Проверяем на wake word
                for wake_word in self.wake_words:
                    if wake_word in text:
                        print(f"✓ Активация по слову: {wake_word}")
                        return self._listen_for_command()
                        
            except queue.Empty:
                continue
    
    def _listen_for_command(self, timeout=5):
        """Слушает команду после активации"""
        print("Слушаю команду...")
        start_time = time.time()
        command_parts = []
        
        while time.time() - start_time < timeout:
            try:
                text = self.audio_queue.get(timeout=1)
                
                # Игнорируем повторные wake words
                if not any(word in text for word in self.wake_words):
                    command_parts.append(text)
                    print(f"Команда: {text}")
                    
                    # Если пауза больше 2 секунд - команда завершена
                    pause_start = time.time()
                    while time.time() - pause_start < 2:
                        try:
                            more_text = self.audio_queue.get(timeout=0.5)
                            if not any(word in more_text for word in self.wake_words):
                                command_parts.append(more_text)
                                pause_start = time.time()  # Сбрасываем таймер паузы
                        except queue.Empty:
                            break
                    
                    break
                    
            except queue.Empty:
                continue
        
        command = " ".join(command_parts).strip()
        return command if command else None
    
    def listen_once(self, timeout=10):
        """Одноразовое прослушивание команды"""
        if not self.is_listening:
            self.start_listening()
        
        return self.wait_for_wake_word(timeout)
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.stop_listening()
        if self.microphone:
            self.microphone.terminate()
        print("Ресурсы очищены")