import json
import re

def count_tokens(response_text, prompt):
    input_tokens = len(prompt.split())
    output_tokens = len(response_text.split())
    return input_tokens, output_tokens


def trim_conversation_history(history, max_tokens=3500):
    total_tokens = sum(len(msg['content'].split()) for msg in history)

    while total_tokens > max_tokens:
        if len(history) > 1:
            removed = history.pop(1)  # Удаляем второе сообщение (сохраняем первое системное)
            total_tokens -= len(removed['content'].split())
        else:
            break


def extract_phone_from_text(text):
    phone_regex = r"(\+?\d{1,4}[^\da-zA-Z]{0,3})?(\(?\d{1,4}\)?[^\da-zA-Z]{0,3})?(\d{1,4}[^\da-zA-Z\d]{0,3}\d{1,4}[^\da-zA-Z\d]{0,3}\d{1,4})"

    match = re.search(phone_regex, text)

    # Проверка на минимальное количество цифр
    if match:
        phone_digits = re.sub(r'\D', '', match.group())  # Убираем все нецифровые символы
        if len(phone_digits) >= 7:  # Проверяем, что цифр в номере хотя бы 7
            print(f"Найден номер телефона: {match.group()}")
            return True
        else:
            print("Ошибка: номер слишком короткий.")
            return False
    else:
        print("Номер телефона не найден.")
        return False

def load_json_data():
    with open('parsed_data_1.json', 'r', encoding='utf-8') as file:
        parsed_data_1 = json.load(file)
    return parsed_data_1