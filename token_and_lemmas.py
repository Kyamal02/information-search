import os
import re
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pymorphy2

# Загрузка необходимых данных для nltk и инициализация pymorphy2 для анализа русского текста
nltk.download('punkt')  # Токенизатор
nltk.download('stopwords')  # Список стоп-слов

morph = pymorphy2.MorphAnalyzer()  # Анализатор pymorphy2 для работы с морфологией русского языка
stop_words = set(stopwords.words('russian'))  # Загрузка стоп-слов для русского языка

def extract_text_from_html(file_path):
    # Функция для извлечения текста из HTML файла
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()  # Получение всего текста без HTML тегов
    return text

def clean_and_tokenize(text):
    # Очистка текста от несловесных символов и токенизация
    text = re.sub(r'\W+', ' ', text)  # Удаление всех несловесных символов
    tokens = word_tokenize(text.lower())  # Приведение к нижнему регистру и токенизация
    # Удаление стоп-слов и проверка, что токен состоит только из кириллических символов
    tokens = [token for token in tokens if token.isalpha() and token not in stop_words and re.match("^[а-яА-ЯёЁ]+$", token)]
    return tokens

def lemmatize(tokens):
    # Лемматизация токенов с помощью pymorphy2
    lemmas = [morph.parse(token)[0].normal_form for token in tokens]
    return lemmas

def process_files(directory):
    # Обработка всех HTML файлов в указанной директории
    all_tokens = set()  # Множество для хранения всех уникальных токенов
    lemmas_dict = {}  # Словарь для группировки токенов по леммам

    for filename in os.listdir(directory):
        print(f"Обработка файла: {filename}")  # Логгирование начала обработки файла
        if filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            text = extract_text_from_html(file_path)
            tokens = clean_and_tokenize(text)
            all_tokens.update(tokens)
            lemmas = lemmatize(tokens)
            for lemma, original in zip(lemmas, tokens):
                if lemma in lemmas_dict:
                    lemmas_dict[lemma].add(original)
                else:
                    lemmas_dict[lemma] = {original}
        print(f"Файл обработан: {filename}")  # Логгирование окончания обработки файла

    # Сохранение уникальных токенов и лемматизированных токенов в файлы
    with open('tokens.txt', 'w', encoding='utf-8') as f:
        for token in sorted(all_tokens):
            f.write(f"{token}\n")

    with open('lemmas.txt', 'w', encoding='utf-8') as f:
        for lemma, original_tokens in sorted(lemmas_dict.items()):
            f.write(f"{lemma} {' '.join(sorted(original_tokens))}\n")

# Укажите актуальный путь к вашим HTML файлам
directory_path = 'D:\\information-search\\downloaded_pages'  # Используйте двойные слэши для Windows путей
process_files(directory_path)
