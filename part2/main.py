# part2_chatbot/main.py
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chatbot import collect_user_info, answer_question
from retrieval import prepare_doc_embeddings

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Create handlers
file_handler = logging.FileHandler('logs/app.log')
console_handler = logging.StreamHandler()

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to root logger
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Get logger for this module
logger = logging.getLogger(__name__)
logger.info("Application starting up")

class ChatMessage(BaseModel):
    messages: list

class QARequest(BaseModel):
    user_info: dict
    question: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Start preparing embeddings in background but don't await here to avoid blocking
        logger.info("Starting document embeddings preparation")
        task = asyncio.create_task(prepare_doc_embeddings())
        # Wait for the task to complete
        await task
        logger.info("Document embeddings preparation completed")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise
    yield

# Initialize FastAPI with lifespan
app = FastAPI(lifespan=lifespan)

@app.post("/collect_info")
async def collect_info(msg: ChatMessage):
    try:
        logger.info("Processing collect_info request")
        reply = await collect_user_info(msg.messages)
        logger.info("Successfully processed collect_info request")
        return {"response": reply}
    except Exception as e:
        logger.error(f"Error in collect_info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(req: QARequest):
    try:
        logger.info(f"Processing question: {req.question}")
        answer = await answer_question(req.user_info, req.question)
        logger.info("Successfully processed question")
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
