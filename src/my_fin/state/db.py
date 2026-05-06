from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from my_fin.config import DATABASE_URL
from my_fin.state.models import Base

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()
