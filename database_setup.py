import os
import sys
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }
    
    
class Item(Base):
    __tablename__ = 'item'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    date = Column(DateTime, default=datetime.now())
    description = Column(String(5000))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    
    @property
    def serialize(self):
        return {
            'cat_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }
    
    
engine = create_engine('sqlite:///categoryitem.db')

Base.metadata.create_all(engine)