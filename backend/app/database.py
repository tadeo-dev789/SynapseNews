from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL,connect_args={"check_same_thread" : False})


SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session
        
