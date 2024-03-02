import os
from bs4 import BeautifulSoup
from collections import defaultdict
import re

def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text.lower()

def create_lemma_mapping(lemmas_file_path):
    lemma_mapping = {}
    with open(lemmas_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            base_lemma, *word_forms = line.strip().split()
            for word_form in word_forms:
                lemma_mapping[word_form] = base_lemma
            lemma_mapping[base_lemma] = base_lemma
    return lemma_mapping

def create_inverted_index(html_files_path, lemma_mapping):
    inverted_index = defaultdict(set)
    for html_file in os.listdir(html_files_path):
        if html_file.endswith('.html'):
            file_path = os.path.join(html_files_path, html_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = extract_text(f.read())
            words = clean_and_extract_words(text)
            page_number = re.search(r'page_(\d+)', html_file).group(1)
            for word in set(words):
                base_lemma = lemma_mapping.get(word, word)
                inverted_index[base_lemma].add(page_number)
    return inverted_index

def clean_and_extract_words(text):
    """Очищает текст и извлекает слова, содержащие только кириллические символы."""
    cleaned_text = re.sub(r'[^а-яА-Я\s]', '', text)  # Оставляет только кириллические символы и пробелы
    cleaned_text = cleaned_text.lower()
    words = cleaned_text.split()
    return words



def evaluate_expression(tokens, inverted_index, lemma_mapping):
    result = set()
    operator = "OR"  # По умолчанию оператор OR для начала выражения

    while tokens:
        token = tokens.pop(0)
        if token == "(":
            sub_result = evaluate_expression(tokens, inverted_index,
                                             lemma_mapping)  # Рекурсивно обрабатываем выражение в скобках
            result = update_result(result, sub_result, operator)
        elif token == ")":
            break  # Выход из текущего уровня рекурсии
        elif token.upper() in {"AND", "OR", "NOT"}:
            operator = token.upper()  # Обновляем оператор
        else:
            # Преобразуем токен в соответствующие страницы
            term = lemma_mapping.get(token.lower(), token.lower())
            current_pages = inverted_index.get(term, set())
            result = update_result(result, current_pages, operator)

    return result


def update_result(current_result, new_pages, operator):
    if operator == "AND":
        return current_result & new_pages if current_result else new_pages
    elif operator == "OR":
        return current_result | new_pages
    elif operator == "NOT":
        return current_result - new_pages

    return current_result


# Функция для разбиения запроса на токены, включая правильное использование лемм
def tokenize_query(query, lemma_mapping):
    tokens = re.findall(r'\(|\)|\w+|\S', query)
    return [lemma_mapping.get(token.lower(), token.lower()) if token not in {"(", ")", "AND", "OR", "NOT"} else token
            for token in tokens]


# Функция поиска, теперь использующая tokenize_query для предварительной обработки запроса
def search_in_inverted_index(query, inverted_index, lemma_mapping):
    tokens = tokenize_query(query, lemma_mapping)
    result_pages = evaluate_expression(tokens, inverted_index, lemma_mapping)
    return result_pages

def save_inverted_index_to_file(inverted_index, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for lemma, pages in sorted(inverted_index.items()):
            pages_str = ' '.join(sorted(pages, key=int))
            file.write(f"{lemma}: {pages_str}\n")



lemmas_file_path = 'lemmas.txt'
html_files_path = 'downloaded_pages/'
inverted_index_file_path = 'inverted_index.txt'


def main():
    lemma_mapping = create_lemma_mapping(lemmas_file_path)
    inverted_index = create_inverted_index(html_files_path, lemma_mapping)


    save_inverted_index_to_file(inverted_index, inverted_index_file_path)


    # Ввод и поиск запросов в консоли
    while True:
        query = input("Введите запрос (или 'exit' для выхода): ").strip()
        if query.lower() == 'exit':
            break
        result_pages = search_in_inverted_index(query, inverted_index, lemma_mapping)
        if result_pages:
            print("Найденные страницы:", sorted(result_pages, key=int))
        else:
            print("Ничего не найдено.")


if __name__ == '__main__':
    main()