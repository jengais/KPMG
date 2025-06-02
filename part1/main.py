# part1/main.py

import gradio as gr
import re
import json

from ocr_client import extract_text_from_file
from gpt_extractor import extract_fields_from_text
from validator import calculate_extraction_stats

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def clean_json_string(response: str) -> dict:
    """
    Cleans and parses a JSON string possibly wrapped in Markdown code block.
    """
    try:
        # Remove triple backticks and optional language identifier
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip())

        # Now parse as JSON
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Error cleaning JSON string: {str(e)}")
        raise


def process_form(file):
    """
    Returns cleaned parsed JSON output.
    """
    try:
        if file is None:
            logger.info("No file provided")
            return None, {
                "total_fields": 0,
                "filled_fields": 0,
                "empty_fields": 0,
                "completion_percentage": 0
            }

        logger.info(f"Processing file: {file}")
        ocr_text = extract_text_from_file(str(file))
        logger.info("OCR text extraction completed")

        extracted_data = extract_fields_from_text(ocr_text)
        logger.info("Field extraction completed")

        parsed_data = clean_json_string(str(extracted_data))
        logger.info("JSON parsing completed")

        # Calculate extraction statistics
        stats = calculate_extraction_stats(parsed_data)
        logger.info(f"Extraction statistics: {stats}")

        return parsed_data, stats
    except Exception as e:
        logger.error(f"Error processing form: {str(e)}")
        raise gr.Error(f"Failed to process form: {str(e)}")


with gr.Blocks() as demo:
    gr.Markdown("### 🧾 ביטוח לאומי Form Field Extractor")
    with gr.Row():
        file_input = gr.File(label="Upload PDF or Image")
    with gr.Row():
        with gr.Column():
            output_json = gr.JSON(label="Extracted Fields")
        with gr.Column():
            stats_output = gr.JSON(label="Extraction Statistics")
    file_input.change(process_form, inputs=file_input, outputs=[output_json, stats_output])

demo.launch()

