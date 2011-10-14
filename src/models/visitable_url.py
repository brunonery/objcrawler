from model_base import Base
from sqlalchemy import Column, Integer, String

class VisitableURL(Base):
    __tablename__ = 'visitable_urls'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    priority = Column(Integer)

    def __init__(self, url, priority):
        self.url = url
        self.priority = priority
