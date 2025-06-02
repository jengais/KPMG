# part1/ocr_client.py

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os
import logging

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

AZURE_FORM_KEY = os.getenv("AZURE_FORM_KEY")
AZURE_FORM_ENDPOINT = os.getenv("AZURE_FORM_ENDPOINT")

if not AZURE_FORM_KEY or not AZURE_FORM_ENDPOINT:
    logger.error("Missing required environment variables for Azure Form Recognizer")
    raise ValueError("Missing required environment variables for Azure Form Recognizer")

try:
    client = DocumentAnalysisClient(
        endpoint=AZURE_FORM_ENDPOINT,
        credential=AzureKeyCredential(AZURE_FORM_KEY)
    )
    logger.info("Successfully initialized Document Analysis Client")
except Exception as e:
    logger.error(f"Failed to initialize Document Analysis Client: {str(e)}")
    raise

def extract_text_from_file(file_path: str) -> str:
    """
    Extracting text from uploaded file.
    Returns raw text.
    """
    try:
        if not file_path or file_path == "None":
            logger.info("No file path provided")
            return ""
            
        logger.info(f"Starting OCR processing for file: {file_path}")
        with open(file_path, "rb") as f:
            poller = client.begin_analyze_document("prebuilt-layout", document=f)
            result = poller.result()

            lines = [line.content for page in result.pages for line in page.lines]
            text = "\n".join(lines)
            logger.info(f"Successfully extracted text from file: {file_path}")
            return text
    except Exception as e:
        logger.error(f"Error during OCR processing: {str(e)}")
        raise
