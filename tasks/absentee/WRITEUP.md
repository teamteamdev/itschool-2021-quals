# Офис: Write-up

В приложениях к заданию видим архив, который можно распаковать. Внутри — несколько директорий, которые сами содержат несколько директорий и т.д., до глубины 6. Названия директорий ни о чём не говорят — «МОЁ», «Новая папка (152)», «резервное», «Пособия», … Внутри находятся файлы нескольких типов. Давайте посмотрим на типы этих файлов. Это можно сделать несколькими способами.

### С помощью средств операционной системы

Можно воспользоваться поиском по файлам во встроенном файловом менеджере, а затем отсортировать их по типу.

### С помощью утилиты `file`

Консольная утилита `file` в Linux позволяет узнать тип файла.

Сначала найдём все файлы командой `find .`. Затем передадим каждый файл в утилиту `file`: `xargs -d '\n' file`.

Чтобы избавиться от упоминания самих имён файлов, добавим флаг `-b`. Также добавим флаг `-i`, чтобы избавиться от лишней информации.

И, наконец, соберём всё вместе и избавимся от повторов с помощью утилиты `sort` с соответствующим флагом:

```bash
$ find . | xargs -d '\n' file -b -i | sort -u
application/msword; charset=binary
application/octet-stream; charset=binary
application/pdf; charset=binary
application/vnd.ms-excel; charset=binary
application/vnd.oasis.opendocument.presentation; charset=binary
application/vnd.oasis.opendocument.spreadsheet; charset=binary
application/vnd.oasis.opendocument.text; charset=binary
application/vnd.openxmlformats-officedocument.wordprocessingml.document; charset=binary
inode/directory; charset=binary
text/html; charset=iso-8859-1
text/html; charset=utf-8
text/plain; charset=us-ascii
```

### Используя расширения файлов

Давайте узнаем расширения всех файлов в директории. Для этого опять же воспользуемся утилитой `find`, но на этот раз уберём директории и оставим только файлы: `find . -type f`.

Чтобы отделить расширение от имени файла, поделим получившиеся строки по символу «.» и возьмём последнюю часть — она и будет расширением.

В Bash довольно сложно взять последнюю часть, поэтому воспользуемся лайфхаком: «перевернём» файл и возьмём первую часть каждой строки, а затем снова перевернём его.

Чтобы перевернуть файл, нам понадобится утилита `rev`. А для взятия части до первой точки — команда `cut -d'.' -f 1`.

Наконец, список расширений снова нужно очистить от дубликатов. Получаем общую команду:

```bash
$ find . -type f | rev | cut -d. -f 1 | rev | sort -u
doc
docx
odp
ods
odt
pdf
xls
 ПК/Адлер/Новая папка (122)/links
```

Проанализируем результат. Нам попались файлы следующих типов:

| Расширение | Mime Type | Тип файла |
|-----|-----|-----|
| `.doc` | `application/msword; charset=binary` | Текстовый документ |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document; charset=binary` | Текстовый документ |
| `.odt` | `application/vnd.oasis.opendocument.text; charset=binary` | Текстовый документ |
| `.odp` | `application/vnd.oasis.opendocument.presentation; charset=binary` | Презентация |
| `.ods` | `application/vnd.oasis.opendocument.spreadsheet; charset=binary` | Таблица |
| `.xls` | `application/vnd.ms-excel; charset=binary` | Таблица |
| `.pdf` | `application/pdf; charset=binary` | Документ |
| — | `inode/directory; charset=binary` | Директория |
| — | `text/plain; charset=us-ascii` | Текстовый файл |
| — | `text/html; charset=iso-8859-1`, `text/html; charset=utf-8`, `application/octet-stream; charset=binary` | Различные документы |

Нам известно, что сотрудник ищет презентацию. В архиве находится всего один файл с нужным расширением (`.odp`) и типом. В нём и находится флаг.

Задачу можно было решить и по-другому — просто перебрать все известные расширения файлов с презентациями и поискать файлы с такими расширениями в архиве.

Флаг: **school_digging_and_discovering_is_a_useful_skill_d2a7a1410465**
