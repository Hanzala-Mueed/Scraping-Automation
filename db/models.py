
from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from database import engine

Base = declarative_base()

class Software(Base):
    __tablename__ = "software"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    description = Column(Text)
    subcategory = Column(String, nullable=True)
    category = Column(String, nullable=True)
    downloads = Column(String, nullable=True)
    size = Column(JSON, nullable=True) 
    download_link = Column(String, nullable=True)
    password = Column(String, nullable=True)

   # Software Title
   #* Post URL
   #* Software Size (Value + Unit)
   #* Version
   #* Release Date (from right sidebar)
   #* Direct Download Button Url



class Categories(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    primary_category = Column(String, nullable=False)
    sub_category = Column(String, nullable=False)
    child_category = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)


