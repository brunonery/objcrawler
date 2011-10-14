from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.model_base import Base

class DatabaseHandler():
    def __init__(self, database_address):
        self.engine_ = create_engine(database_address)
        self.session_maker_ = sessionmaker(bind=self.engine_)

    def Init(self):
        # Create all tables that don't exist.
        Base.metadata.create_all(self.engine_)

    def CreateSession(self):
        return self.session_maker_()
