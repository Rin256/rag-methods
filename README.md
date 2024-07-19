# Инструкция по работе с приложением

1. Установить Microsoft C++ Build Tools (https://github.com/bycloudai/InstallVSBuildToolsWindows?tab=readme-ov-file)

2. Установить зависимости для python согласно файлу `requirements.txt`
```python
pip install -r requirements.txt
```

3. Настроить OpenAPI
    - Настроить VPN
    - Пополнить аккаунт OpenAPI (https://platform.openai.com/, не путать с https://chatgpt.com/)
    - Создать файл .env и указать в нем OpenAPI ключ, аналогично примеру из .env.example

4. Поместить markdown файлы в каталог 'data' и создать векторную базу данных Chroma DB
```python
python chroma_generator.py
```

5. Задавать вопросы по markdown файлам
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
