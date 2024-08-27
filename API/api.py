from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from ocr import pdf_to_text
from classifier import ml_classification_pipeline
from features_extraction_chatgpt import chatgpt_pipeline
from utils import read_s3_document, get_secret, check_file_exists
import shutil

SECRET_DICT = get_secret()
BUCKET_NAME = SECRET_DICT['BUCKET_CLASSIFIER']
BUCKET_FILES = SECRET_DICT['BUCKET_FILES']
CHATGPT_API_KEY = SECRET_DICT['CHATGPT_API_KEY']

# Configuration settings
CORS_SETTINGS = {
    "allow_origins": "*",
    "allow_credentials": False,
    "allow_methods": ["POST"],
    "allow_headers": ["x-apigateway-header", "Content-Type", "X-Amz-Date"],
}

app = FastAPI(title='PDF Classification API')
app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
handler = Mangum(app)

@app.post("/v1/text_extractor", status_code=200)
async def extract_text(file: UploadFile = File(...)):
    # Save the uploaded file
    file_location = f"/tmp/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Perform OCR on the saved file
    extracted_text = pdf_to_text(file_location)
    
    return {"error": False, "extracted_text": extracted_text}

@app.post("/v2/text_extractor", status_code=200)
async def extract_text(request: Request):

    requests = await request.json()

    s3Id = requests['s3Id']
    results = check_file_exists(s3Id, BUCKET_FILES)

    if results.get('error'):
        return results.get('message')
    else:
        pdf_file = read_s3_document(s3Id, BUCKET_FILES)
        # Perform OCR on the saved file
        extracted_text = pdf_to_text(pdf_file)
        return {"error": False, "extracted_text": extracted_text}

@app.post("/v1/ml_classifier", status_code=200)
async def classify_pdf(request: Request):
    requests = await request.json()

    text = requests['extracted_text']
    predictions = ml_classification_pipeline(text, BUCKET_NAME)

    return {"error": False, "prediction": predictions}

@app.post("/v1/chatgpt_extraction", status_code=200)
async def extract_with_chatgpt(request: Request):
    requests = await request.json()

    text = requests['text']
    document_type = requests['document_type']

    if document_type not in [0, 1, 2, 3]:
        return {
        'Error': False, 
        'message': (
            "Please choose a value from 0 to 3, where:\n"
            "0 -> certifications\n"
            "1 -> DPE\n"
            "2 -> fichier descriptif\n"
            "3 -> rapport d'expertise"
        )
    }

    results = chatgpt_pipeline(text, document_type, CHATGPT_API_KEY)

    return {"error": False, 'results': results}
