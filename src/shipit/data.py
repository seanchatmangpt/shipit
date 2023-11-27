import os

from sqlalchemy import create_engine
from sqlmodel import Session

from utils.chroma_memstore import ChromaMemStore

current_dir = os.path.dirname(os.path.abspath(__file__))


db_path = os.path.join(current_dir, "dev.db")
mem_store_path = os.path.join(current_dir, "mem_store")

DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL)


def get_mem_store():
    return ChromaMemStore(mem_store_path)


def get_session():
    return Session(engine)
