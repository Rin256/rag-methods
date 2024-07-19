from fastapi import FastAPI
from pydantic import BaseModel
from assistant import Assistant
import uvicorn
from dotenv import load_dotenv

class AssistantAPI:
    def __init__(self):
        self.app = FastAPI()
        self.assistant = Assistant()
        self.setup_routes()

    def setup_routes(self):
        # Маршрут для генерации ответа на основе запроса
        @self.app.post("/generate")
        def generate(query_model: QueryModel):
            result = self.assistant.generate(query_model.question)
            return {"result": result}

class QueryModel(BaseModel):
    question: str

if __name__ == "__main__":
    # Загрузка переменных окружения из файла .env
    load_dotenv()
    
    # Создание экземпляра API и запуск сервера
    api = AssistantAPI()
    uvicorn.run(api.app, host="0.0.0.0", port=8000)
