#!/usr/bin/env python3

import copy
import io
import hmac
import json
import os
import pathlib
import random
import shutil
import sys
import zipfile

PREFIX = "school_digging_and_discovering_is_a_useful_skill_"
SECRET = b"nsvbdueh8q0439r203y8guewhuxszfbr5nb9b0nenrww"
SALT_SIZE = 12

TOP_FOLDERS = ["МОЁ", "РАБОТА", "Мои документы", "ОФИС", "ФЛЕШКА"]

FOLDERS = ["шабашки", "скачал", "бланки", "ццц", "СКАЧКА", "субконтракты", "рабочий стол", "мусор",
           "копия", "планирование", "с флэшки", "РАБОТА", "по работе", "рабочая", "офис", "боссу",
           "отчётность", "flash", "моё", "сына", "любимая", "НОВЫЕ ФАЙЛЫ", "Новая папка",
           "untitled folder", "ОТПУСК", "фотографии", "Адлер", "Сочи", "Анапа", "Геленджик",
           "Кубань 2016", "хоста", "Мацеста", "Туапсе", "Абхазия", "Гагра", "ИБ", "регламенты",
           "практика", "Инструктаж", "Инструктаж новый", "Тесты", "на подпись", "Документы ИНЕТ",
           "ДОКУМЕНТЫ ТАТЬЯНА", "Анна", "Документы для Дарьи Сергеевны", "важные доки", "бухучет",
           "на проверку", "Налоговая", "Презентации и др.", "Сложить сюда папки", "Аттестация",
           "Английский", "Образование", "ДЕНИСУ", "Срочно", "Переделать СРОЧНО", "для сайта",
           "иллюстрации", "Аналитика", "Дом. ПК", "Копия", "резервное", "годовой", "премии", "ок",
           "удалить", "Корзина", "ПАСЬЯНСЫ", "инструкции", "пособия", "Статьи", "черновики",
           "Учебники", "Функциональные", "Учебные программы", "ВКР", "для выпуска", "гиа",
           "рабочие программы", "выложить", "из вотсаппа", "вайбер", "флешка зеленая", "разное",
           "отдать продажникам", "эл.почта", "Разобрать", "папка", "моя", "Файлы", "Важное",
           "Проверить на вирусы", "Про компьютеры Сыну", "Школа", "Минобр", "Сохранить", "Другое",
           "Потом","Temp", "tmp", "Мусор", "Архив", "Полезно", "Памятки", "Макеты", "__", "Нужно",
           "Проекты документов", "На подписи", "Подписано", "Разослать", "Шаблоны", "Примеры"] + \
          [f"{grade} класс" for grade in range(1, 12)] + \
          [f"{year}" for year in range(2007, 2021)] + \
          [f"Новая папка ({x})" for x in range(2, 200)]

# sum(LEVELS) == len(FOLDERS)
LEVELS = [12, 27, 52, 98, 150]


def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    target_dir = sys.argv[2]
    flag = get_flag()
    random.seed(int(flag.encode().hex(), 16))

    source_file = os.path.join("private", "files.zip")
    slides_file = os.path.join("private", "pres.odp")
    target_file = os.path.join(target_dir, "Рабочий стол.zip")

    with zipfile.ZipFile(target_file, "w") as zf:
        folders = copy.copy(FOLDERS)
        random.shuffle(folders)

        folders_by_level = [[
            pathlib.Path(folder)
            for folder in TOP_FOLDERS
        ]]

        used = 0

        for level in LEVELS:
            previous_level = folders_by_level[-1]
            new_level = []

            for item in folders[used:used+level]:
                prefix = random.choice(previous_level)
                new_level.append(prefix / item)
                zipinfo = zipfile.ZipInfo(new_level[-1].as_posix() + "/", (1984, 12, 30, 12, 0, 0))
                zipinfo.external_attr = 16
                zf.writestr(zipinfo, "")

            used += level
            folders_by_level.append(new_level)

        with zipfile.ZipFile(source_file, "r") as zf_source:
            for item in zf_source.infolist():
                prefix = random.choice(folders_by_level[-1])
                zf.writestr(
                    zipfile.ZipInfo(
                        filename=(prefix / item.filename).as_posix(),
                        date_time=item.date_time
                    ),
                    zf_source.open(item).read()
                )

        slides = io.BytesIO()
        with zipfile.ZipFile(slides_file, "r") as zp_source:
            with zipfile.ZipFile(slides, "w") as zp_target:
                for f in zp_source.infolist():
                    data = zp_source.open(f).read()
                    if f.filename == "content.xml":
                        data = data.replace(b"+++FLAG+++", flag.encode())
                    zp_target.writestr(f, data)

        slides_path = random.choice(folders_by_level[-1]) / "Годовой план шефу.odp"
        zf.writestr(
            zipfile.ZipInfo(
                filename=slides_path.as_posix(),
                date_time=(2017, 4, 17, 13, 35, 27)
            ),
            slides.getvalue()
        )

    json.dump({"flags": [flag], "substitutions": {"path": slides_path.as_posix()}, "urls": []}, sys.stdout)


if __name__ == "__main__":
    generate()
