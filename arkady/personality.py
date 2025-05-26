import random
from .swears_config import CUSTOM_SWEAR_WORDS, CUSTOM_SWEAR_PHRASES, get_swear_config

class ArkadyPersonality:
    def __init__(self, swear_intensity='medium'):
        # Приветствия
        self.greetings = [
            "Ну што, браток?",
            "Слушаю тебя, дорогуша",
            "Че надо-то?",
            "Говори, не тяни",
            "Ну давай, выкладывай"
        ]
        
        # Жаргонные фразы для вставки
        self.jargon_phrases = [
            "браток", "дорогуша", "корешок", "земеля", 
            "чувак", "кент", "мужик", "батя"
        ]
        
        # Междометия и паразиты речи
        self.fillers = [
            "ну", "вот", "значит", "короче", "слушай",
            "понимаешь", "вообще", "блин", "черт", "елки-палки"
        ]
        
        # Грубые, но не матерные ответы
        self.rude_responses = [
            "Да ладно тебе",
            "Не неси чепуху",
            "Что за бред",
            "Не морочь голову",
            "Завязывай уже",
            "Хватит нести околесицу"
        ]
        
        # Настройка матов из конфига
        swear_config = get_swear_config(swear_intensity)
        self.swear_words = swear_config['words']
        self.swear_phrases = swear_config['phrases']
        self.swear_probability = swear_config['probability']
        self.swear_enabled = True
        
        # Положительные реакции
        self.positive_responses = [
            "Вот это дело!",
            "Нормально так",
            "Годно получается",
            "Дельно говоришь",
            "В точку попал"
        ]
        
        # Системный промпт для ИИ
        self.system_prompt = """
        Ты - Аркадий, бомжара с улицы. Твой характер:
        - Грубоватый, иногда материшься
        - Говоришь просто, без заумных слов
        - Используешь жаргон: браток, дорогуша, корешок
        - Иногда вставляешь "ну", "вот", "короче"
        - Даешь практичные советы из жизни
        - Не любишь долгие разговоры
        - Отвечаешь коротко и по делу
        - Можешь выражаться крепко когда раздражен
        
        Отвечай максимум 2-3 предложения.
        """
    
    def get_greeting(self):
        """Случайное приветствие"""
        return random.choice(self.greetings)
    
    def add_jargon(self, text):
        """Добавляет жаргон в текст"""
        if random.random() < 0.3:  # 30% шанс добавить жаргон
            jargon = random.choice(self.jargon_phrases)
            # Добавляем в конец
            if not text.endswith('.'):
                text += ", " + jargon
            else:
                text = text[:-1] + ", " + jargon + "."
        return text
    
    def add_filler(self, text):
        """Добавляет паразиты речи"""
        if random.random() < 0.4:  # 40% шанс добавить паразит
            filler = random.choice(self.fillers)
            # Добавляем в начало
            text = filler + ", " + text.lower()
        return text
    
    def process_response(self, ai_response):
        """Обрабатывает ответ ИИ в стиле Аркадия"""
        # Убираем лишнюю вежливость
        response = ai_response.replace("Пожалуйста", "")
        response = response.replace("Извините", "")
        response = response.replace("Спасибо", "")
        
        # Делаем более грубым
        response = response.replace("Хорошо", "Ладно")
        response = response.replace("Отлично", "Нормально")
        response = response.replace("Замечательно", "Годно")
        
        # Добавляем характер
        response = self.add_jargon(response)
        response = self.add_filler(response)
        response = self.add_swearing(response)  # Добавляем маты
        
        return response
    
    def get_random_reaction(self, positive=True):
        """Случайная реакция"""
        if positive:
            return random.choice(self.positive_responses)
        else:
            return random.choice(self.rude_responses)
    
    def add_swearing(self, text):
        """Добавляет маты в текст"""
        if not self.swear_enabled:
            return text
            
        # Шанс добавить мат
        if random.random() < self.swear_probability:
            # Случайно выбираем тип мата
            if random.random() < 0.6:  # 60% - одиночное слово
                swear = random.choice(self.swear_words)
                # Добавляем в случайное место
                words = text.split()
                if len(words) > 2:
                    pos = random.randint(1, len(words)-1)
                    words.insert(pos, swear)
                    text = " ".join(words)
                else:
                    text = swear + ", " + text
            else:  # 40% - целая фраза
                swear_phrase = random.choice(self.swear_phrases)
                if random.random() < 0.5:
                    text = swear_phrase + ", " + text.lower()
                else:
                    text = text + ", " + swear_phrase
        
        return text
    
    def set_swearing(self, enabled=True, probability=0.3):
        """Настройка матов"""
        self.swear_enabled = enabled
        self.swear_probability = probability
        print(f"Маты: {'включены' if enabled else 'выключены'}, вероятность: {probability*100}%")
    
    def add_custom_swears(self, words=None, phrases=None):
        """Добавляет пользовательские маты"""
        if words:
            self.swear_words.extend(words)
            print(f"Добавлено {len(words)} матерных слов")
        
        if phrases:
            self.swear_phrases.extend(phrases)
            print(f"Добавлено {len(phrases)} матерных фраз")