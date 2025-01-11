import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database import SessionLocal
from datetime import datetime
from models import Question_Answer

session = SessionLocal()

def insert_QandA(json_data):
    # Iterate through the JSON data and insert each record into the database
    try : 
        for item in json_data:
            new_question_answer = Question_Answer(
                question=item["question"],
                answer=item["answer"]
            )
            session.add(new_question_answer)

        # Commit the changes to the database
        session.commit()

        # Close the session
        session.close()

        return 'Data Upload Success'
    except Exception as e:
        return 'Data Upload Failed' 