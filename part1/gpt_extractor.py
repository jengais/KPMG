# part1_form_extraction/gpt_extractor.py

from openai import AzureOpenAI
import os
import logging

from schema import eng_form_template, structured_data_prompt_template

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

if not all([AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION, DEPLOYMENT_NAME]):
    logger.error("Missing required environment variables for Azure OpenAI")
    raise ValueError("Missing required environment variables for Azure OpenAI")

try:
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )
    logger.info("Successfully initialized Azure OpenAI client")
except Exception as e:
    logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
    raise

def extract_fields_from_text(raw_text: str) -> dict:
    """
    Extracting and filling all JSON field according to schema.
    """
    try:
        if not raw_text:
            logger.warning("Empty text provided for field extraction")
            return {}

        logger.info("Starting field extraction from text")

        prompt = structured_data_prompt_template.format(
            raw_text=raw_text,
            eng_form_template=eng_form_template
        )

        logger.info("Sending request to Azure OpenAI")
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0.1,
            top_p=1.0,
        )

        result = response.choices[0].message.content
        logger.info("Successfully received response from Azure OpenAI")
        return result

    except Exception as e:
        logger.error(f"Error during field extraction: {str(e)}")
        raise