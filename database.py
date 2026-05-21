import os

from dotenv import load_dotenv
from sqlmodel import create_engine, Session

load_dotenv()
DATABASE_URL = os.getenv("CONNECTION_STRING")
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300
)


def get_session():
    with Session(engine) as session:
        yield session
