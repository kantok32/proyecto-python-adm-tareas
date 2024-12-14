from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .task_model import Base  # Aquí importamos Base

def get_session(db_path):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)  # Asegúrate de que `Base` esté correctamente definido
    Session = sessionmaker(bind=engine)
    return Session()