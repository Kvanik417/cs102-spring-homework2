from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()
engine = create_engine("sqlite:///news.db")
session = sessionmaker(bind=engine)


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    complexity = Column(String)
    habr_id = Column(String)
    label = Column(String)


Base.metadata.create_all(bind=engine)
