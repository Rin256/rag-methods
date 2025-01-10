# Инструкция по работе с приложением

## Описание
Приложение служит для поиска информации в файлах.
Для работы требуется каталог md файлов и интересующий вопрос.
Результатом служит ответ gpt и список схожих файлов.

## Рекомендации
Виртуальное окружение python позволит избежать ситуаций, когда разные приложения требуют разных пакетов.
Также это предотвращает загрязнение глобального каталога пакетов.
```cli
python -m venv venv :: Создание виртуального окружения
.\venv\Scripts\activate :: Подключение к виртуальному окружению
deactivate :: Отключение от вирутуального окружения
```

## Настройка окружения
1. Установить Microsoft C++ Build Tools (https://github.com/bycloudai/InstallVSBuildToolsWindows?tab=readme-ov-file)
2. Установить Python 3.12 (https://www.python.org/downloads/)
3. Установить зависимости для Python согласно файлу `requirements.txt`
```cli
pip install -r requirements.txt
```
4. Создать файл '.env', где указать OpenAPI ключ и прокси аналогично примеру '.env.example'

## Подготовка данных
1. Поместить markdown файлы в каталог 'data' и создать векторную базу данных Chroma DB
```python
python chroma_generator.py
```

## Поиск информации
**Через консоль**:
```python
python assistant.py "вопрос"
```

**Через API**:
Запустить сервер с API
```python
python server.py
```

Запрос: POST http://127.0.0.1:8000/generate
```json
{
    "question": "вопрос"
}
```

Ответ:
```json
{
    "result": "ответ"
}
```
