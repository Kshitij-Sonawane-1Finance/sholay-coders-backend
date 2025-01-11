from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, false
from sqlalchemy.orm import relationship
from database import Base, engine  
from datetime import datetime

class Model_Accuracy(Base):
    __tablename__ = 'model_accuracy'
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String, unique=False, nullable=True)
    accuracy = Column(Numeric, unique=False, nullable=True)  
    model_url = Column(String, unique=True, nullable=False)
    date_time = Column(DateTime, default=datetime.now())  


class Question_Answer(Base):
    __tablename__ = 'question_answer'
    
    id = Column(Integer, primary_key=True)
    question = Column(String, unique=False, nullable=True)
    answer = Column(String, unique=False, nullable=True)  
    model_id = Column(Integer, unique=False, nullable=True)
    date_time = Column(DateTime, default=datetime.now())  


class Model_Question(Base):
    __tablename__ = 'model_question'
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, unique=False, nullable=True)
    question_id = Column(Integer, unique=False, nullable=True)  
    status = Column(Boolean, default=false)  

# Create the table in the database
Base.metadata.create_all(engine)
