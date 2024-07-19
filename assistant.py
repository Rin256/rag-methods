import argparse
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import openai
from dotenv import load_dotenv
import os

class Assistant:
    PROMPT_TEMPLATE = """
Ты помощник для ответов на вопросы сотрудников компании 1С-ИЖТИСИ.
Не придумывай ответ. Если не знаешь ответа, просто скажи: «Не удалось найти ответ в предоставленных источниках.»
Отвечай на вопрос, основываясь только на следующем контексте:

{context}

---

Ответь на вопрос, исходя из приведенного выше контекста: {question}
"""
    def __init__(self, chroma_path="chroma"):
        openai.api_key = os.environ['OPENAI_API_KEY']
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-large")
        self.db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)
        self.chroma_path = chroma_path

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
        chunks = self.db.similarity_search_with_relevance_scores(question, k=3)
        return chunks
    
    def create_prompt(self, chunks, question):
        # Создание промпта из шаблона
        context = "\n\n---\n\n".join([chunk.page_content for chunk, _score in chunks])
        prompt_template = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)
        return prompt_template.format(context=context, question=question)

    def get_response(self, prompt):
        # Генерация ответа с использованием модели
        model = ChatOpenAI(model="gpt-4o", temperature=0.2)
        return model.invoke(prompt).content

    def format_response(self, response, chunks):
        # Форматирование текста ответа с указанием источников
        sources = [chunk.metadata.get("source", None) for chunk, _score in chunks]
        return f"{response}\n\nИсточники: {sources}"

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
