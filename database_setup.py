import os
import sys
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    
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
    # Implement the cascade property
    category = relationship(Category, cascade="delete")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    
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