import os
import re


def get_text(filename):
    filepath = os.path.join("static/texts", filename)
    with open(filepath, "r") as f:
        text = f.read()
    return text


def parse_int(msg: str) -> int | None:
    s = msg.lstrip()
    if s and s[0].isdigit():
        num_str = ""
        for char in s:
            if char.isdigit():
                num_str += char
            else:
                break
        return int(num_str)


def parse_id(msg: str) -> int | None:
    # Строка начинается с числа
    if result := parse_int(msg):
        return result

    # Поиск ссылки
    pattern = r"\/players\/(\d+)"
    search_result = re.search(pattern, msg)
    if not search_result:
        return None
    try:
        result = int(search_result.group(1))
        return result
    except ValueError:
        return None

def get_valid_initials(msg: str) -> str | None:
    # Удаляем знаки препинания
    msg_cleaned = re.sub(r"[^\w\s]", "", msg)
    # Регулярное выражение для проверки 1-2 слов на русском языке без чисел
    pattern = r"^(?:[а-яА-ЯЁё]+(?:\s+[а-яА-ЯЁё]+)?)?$"

    if re.match(pattern, msg_cleaned):
        return msg_cleaned.strip()  # Возвращаем очищенное сообщение
    return None  # Если не соответствует, возвращаем None
