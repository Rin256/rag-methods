import os
import shutil
from dotenv import load_dotenv

import openai
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from config import DATA_DIR, CHROMA_DIR

class ChromaGenerator:
    def __init__(self):
        openai.api_key = os.environ['OPENAI_API_KEY']
        self.chroma_path = CHROMA_DIR
        self.data_path = DATA_DIR

    def generate(self):
        # Основной метод для генерации хранилища данных
        documents = self.load_documents()
        chunks = self.split_text(documents)
        self.attach_metadata_to_chunks(chunks)
        self.save_to_chroma(chunks)

    def load_documents(self):
        # Загрузка документов из директории
        loader = DirectoryLoader(self.data_path, glob="*.md")
        documents = loader.load()
        return documents

    def split_text(self, documents: list[Document]):
        # Разделение текстов документов на чанки
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000,
            chunk_overlap=1000,
            length_function=len,
            add_start_index=True,
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Разделено {len(documents)} документов на {len(chunks)} чанков.")
        return chunks
    
    def attach_metadata_to_chunks(self, chunks):
        for chunk in chunks:
            metadata_path = chunk.metadata['source'].replace('.md', '.json')
            if not os.path.exists(metadata_path):
                continue
            with open(metadata_path, "r", encoding="utf-8") as file:
                metadata = file.read()
                chunk.page_content = f'{metadata}\n\n{chunk.page_content}'

    def save_to_chroma(self, chunks: list[Document]):
        # Очистка предыдущей базы данных, если она существует
        if os.path.exists(self.chroma_path):
            shutil.rmtree(self.chroma_path)
        
        # Создание новой базы данных из документов
        embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")
        db = Chroma.from_documents(
            chunks, 
            embedding_function, 
            persist_directory=self.chroma_path, 
            collection_metadata={"hnsw:space": "cosine"}
        )

        print(f"Сохранено {len(chunks)} чанков в {self.chroma_path}.")

if __name__ == "__main__":
    # Загрузка переменных окружения из файла .env
    load_dotenv()
    
    # Создание экземпляра ChromaGenerator и запуск процесса генерации
    generator = ChromaGenerator()
    generator.generate()
