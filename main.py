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

def extract_question_from_file(name, url, file_path, file_extension):
    if file_extension == '.csv':
        df = pd.read_csv(file_path) 
    else:
        df = pd.read_excel(file_path, engine='openpyxl')
    questions_answers = df[['question', 'answers']].to_dict(orient='records')
    json_data = json.dumps(questions_answers, indent=4)
    print(json_data)
    return questions_answers

            
def generate_questions(name, url, text, count):
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
async def upload_file(name: str,url:str, dynamic: bool, count:str, file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    else:
        folder_path = "uploads"

        if os.listdir(folder_path):
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        destination = f"{folder_path}/{file.filename}"
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_extension = os.path.splitext(destination)[1].lower()
        
        if file_extension == '.pdf' and dynamic:
            pdfText = extract_text_from_pdf(destination)
            if pdfText:
                pdfText = generate_questions(name, url, pdfText, count)
                return pdfText
            else:
                raise HTTPException(status_code=400, detail="PDF text extraction failed.")
        elif file_extension in ['.xls', '.xlsx', '.csv'] and not dynamic: 
            pdfText = extract_question_from_file(name, url, destination, file_extension)
            return pdfText
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")
        
@app.post("/analyze_model",)
async def analyze_model():
    return {"message": "Welcome to Sholay Coders!"}

@app.post("/model_overview",)
async def model_overview():
    return {"message": "Welcome to Sholay Coders!"}

@app.post("/dashboard",)
async def dashboard():
    return {"message": "Welcome to Sholay Coders!"}