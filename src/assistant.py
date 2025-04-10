import argparse
import csv
import json
import os
import re
import uuid
from datetime import datetime

from dotenv import load_dotenv
from filelock import FileLock
import openai
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate

from config import LOGS_DIR, CHROMA_DIR

class Assistant:
    NEGATIVE_ANSWER = "Не удалось найти ответ."
    PROMPT_TEMPLATE = f"""Ты помощник для поиска подходящих методов.
Ответь на вопрос, основываясь только на следующем контексте:

{{context}}

---

Ответь на вопрос, исходя из приведенного выше контекста: {{question}}
Если контекст не содержит ответа, просто скажи: «{NEGATIVE_ANSWER}»"""
    
    def __init__(self):
        openai.api_key = os.environ['OPENAI_API_KEY']
        embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")
        self.db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding_function)
        self.log_dir = LOGS_DIR
        os.makedirs(self.log_dir, exist_ok=True)

    def generate(self, question):
        # Основная логика для поиска в базе данных и генерации ответа
        chunks = self.search_database(question)
        prompt = self.create_prompt(chunks, question)
        response = self.get_response(prompt)
        formatted_response = self.format_response(response, chunks)
        print(formatted_response)
        return formatted_response

    def search_database(self, question):
        # Поиск в базе данных релевантных документов
        chunks = self.db.similarity_search_with_relevance_scores(question, k=10)
        return chunks

    def create_prompt(self, chunks, question):
        # Создание промпта из шаблона
        context = "\n\n---\n\n".join([chunk.page_content for chunk, _score in chunks])
        prompt_template = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)
        return prompt_template.format(context=context, question=question)

    def get_response(self, prompt):
        # Генерация ответа с использованием модели
        model = ChatOpenAI(model="gpt-4o", temperature=1)
        response = model.invoke(prompt)

        # Получение информации о запросе
        input_tokens = response.response_metadata['token_usage']['prompt_tokens']
        output_tokens = response.response_metadata['token_usage']['completion_tokens']
        total_tokens = response.response_metadata['token_usage']['total_tokens']
        model_name = response.response_metadata['model_name']

        # Получение текущей даты и времени
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Генерация уникального идентификатора
        unique_id = str(uuid.uuid4())

        # Запись информации в CSV файл
        csv_file_path = os.path.join(self.log_dir, "query_logs.csv")
        data = [unique_id, current_time, input_tokens, output_tokens, total_tokens, model_name]
        self.write_to_csv(csv_file_path, data)

        # Запись вопроса и ответа в JSON файл
        log_data = {
            "prompt": prompt,
            "response": response.content
        }
        json_file_path = os.path.join(self.log_dir, f"{unique_id}.json")
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(log_data, json_file, ensure_ascii=False, indent=4)

        return response.content

    def write_to_csv(self, file_path, data):
        lock = FileLock(f"{file_path}.lock")
        with lock:
            file_exists = os.path.isfile(file_path)
            with open(file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    # Записываем заголовок, если файл создается впервые
                    writer.writerow(["id", "date", "input_tokens", "output_tokens", "total_tokens", "model_name"])
                writer.writerow(data)

    def format_response(self, response, chunks):
        # Форматирование текста ответа с указанием источников
        sources = [self.format_source(chunk.metadata.get("source", None)) for chunk, _score in chunks]
        return f"{response}\n\nИсточники:\n{"\n".join(sources)}"

    def format_source(self, source):
        # Проверяем, есть ли ссылка и соответствует ли она ожидаемому формату
        if source and re.match(r".*data\\.*\.md", source):
            # Преобразуем путь к нужному формату
            # Убираем 'data\\' и '.md' и заменяем разделители
            formatted_source = re.sub(r'.*data\\', '', source)
            formatted_source = formatted_source.replace('.md', '')
            return formatted_source
        return source

if __name__ == "__main__":
   # Загрузка переменных окружения из файла .env
   load_dotenv()

   # Чтение текста запроса
   parser = argparse.ArgumentParser()
   parser.add_argument("question", type=str, help="The query text.")
   args = parser.parse_args()
   question = args.question

   # Создание экземпляра Assistant и его запуск
   assistant = Assistant()
   assistant.generate(question)
