import os
import PyPDF2
import shutil
import random
import json
import pandas as pd

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException,File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()
app = FastAPI()

def _get_random_api_key():
    api_keys = os.getenv('GEMINI_API_KEY').split(',')
    if not api_keys:
        raise HTTPException(status_code=400, detail="No API keys available")
    key = random.choice(api_keys)
    print(f"Selected API key: {key}")
    if not key:
        raise HTTPException(status_code=400, detail="Failed to fetch API key")
    return key

gemini_api_key = _get_random_api_key()
model_name = os.getenv('MODEL_NAME')

# Initialize the language model
llm = GoogleGenerativeAI(model=model_name,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=gemini_api_key)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; modify as needed for specific domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

def extract_text_from_pdf(file_path):
    pdf_reader = PyPDF2.PdfReader(file_path)
    if not pdf_reader:
        raise HTTPException(status_code=400, detail="PDF file not found")
    else :
        if pdf_reader.is_encrypted:
            raise HTTPException(status_code=400, detail="PDF file is encrypted")
        else:
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
    return text

def extract_question_from_file(file_path, file_extension):
    if file_extension == '.csv':
        df = pd.read_csv(file_path) 
    else:
        df = pd.read_excel(file_path, engine='openpyxl')
    questions_answers = df[['question', 'answers']].to_dict(orient='records')
    json_data = json.dumps(questions_answers, indent=4)
    print(json_data)
    return questions_answers

            
def generate_questions(text, count):
    try :
        template = """
        You are Question Answer Generation Expert who is expert in question generation and is proficient in creating detailed and well-explained answers.
        Please generate a JSON object containing a list of {count} questions from {text}. 
        
        The JSON should include following properties:
        
        question: A string representing the question .
        answer: A string representing the answer.
        """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        responses =  chain.invoke({"text": text, "count": count})
        responseString = responses.replace("```json", "").replace("```", "").strip()
        json_data = json.loads(responseString)
        return json_data
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error generating questions: {e}")
    
@app.post("/upload_file",)
async def upload_file(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    else:
        destination = f"uploads/{file.filename}"
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_extension = os.path.splitext(destination)[1].lower()
        if file_extension == '.pdf':
            pdfText = extract_text_from_pdf(destination)
            if pdfText:
                pdfText = generate_questions(pdfText, 5)
                return pdfText
            else:
                raise HTTPException(status_code=400, detail="PDF text extraction failed.")
        elif file_extension in ['.xls', '.xlsx', '.csv']: 
            pdfText = extract_question_from_file(destination, file_extension)
            return pdfText
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")
        
    

# if __name__ == "__main__":
#     try:
#         file_path = "/Users/imsuraj/Projects/Hackathon/sholay-coders-backend/Untitled spreadsheet.xlsx"
#         # file_path = "/Users/imsuraj/Projects/Hackathon/sholay-coders-backend/tax_questions.csv"
#         # file_path = "/Users/imsuraj/Projects/Hackathon/sholay-coders-backend/Model Governance Analysis.pdf"
#         file_extension = os.path.splitext(file_path)[1].lower()
#         if file_extension == '.pdf':
#             pdfText = extract_text_from_pdf(file_path)
#             if pdfText:
#                 generate_questions(pdfText, 5)
#             else:
#                 raise HTTPException(status_code=400, detail="PDF text extraction failed.")
#         elif file_extension in ['.xls', '.xlsx', '.csv']: 
#             pdfText = extract_question_from_file(file_path, file_extension)
#         else:
#             raise HTTPException(status_code=400, detail="Unsupported file format.")
        
#     except Exception as e:
#         print(e)




