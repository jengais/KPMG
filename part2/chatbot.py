# part2_chatbot/chatbot.py

import logging
import os
from openai import AsyncAzureOpenAI
from prompts import collect_info_prompt, qa_prompt_template
from retrieval import retrieve_relevant_chunks
from dotenv import load_dotenv
load_dotenv()

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/chatbot.log'),
        logging.StreamHandler()  # This will also print to console
    ]
)
logger = logging.getLogger(__name__)

# Test logging
logger.info("Chatbot module initialized")

api_key = os.getenv("AZURE_OPENAI_KEY")
api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

client = AsyncAzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=api_base
)

async def collect_user_info(messages):
    try:
        logger.info("Starting user info collection")
        response = await client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[{"role": "system", "content": collect_info_prompt}] + messages,
            temperature=0.3,
            top_p=0.9,
            max_tokens=256,
        )
        logger.info("Successfully collected user info")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in collect_user_info: {str(e)}", exc_info=True)
        raise

async def answer_question(user_info, question):
    try:
        logger.info(f"Processing question for user: {user_info.get('hmo', 'unknown')} - {user_info.get('tier', 'unknown')}")
        relevant_chunks = await retrieve_relevant_chunks(question, top_k=3)
        context = "\n\n".join(relevant_chunks)

        print(context)

        prompt = qa_prompt_template.format(
            context=context,
            hmo=user_info["hmo"],
            tier=user_info["tier"],
            question=question
        )

        response = await client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.0,
            top_p=1.0,
            max_tokens=1024,
        )
        logger.info("Successfully generated answer")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in answer_question: {str(e)}", exc_info=True)
        raise

