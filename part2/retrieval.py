
import os
import logging
import aiofiles
from bs4 import BeautifulSoup
from openai import AsyncAzureOpenAI
import tiktoken
import numpy as np
from scipy.spatial.distance import cosine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging setup
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/retrieval.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Token-based chunking config
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Azure OpenAI config
api_key = os.getenv("AZURE_OPENAI_KEY")
api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

# OpenAI client
client = AsyncAzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=api_base
)

# Tokenizer
tokenizer = tiktoken.encoding_for_model(AZURE_OPENAI_EMBEDDING_DEPLOYMENT)

# Global state
doc_chunks = []
doc_embeddings = None

# HTML to structured plain text
def extract_structured_text(html):
    soup = BeautifulSoup(html, "html.parser")
    parts = []

    def clean_text(text):
        return ' '.join(text.strip().split())

    # Convert tables to markdown-like format
    for table in soup.find_all("table"):
        headers = [clean_text(th.get_text()) for th in table.find_all("th")]
        rows = []
        for tr in table.find_all("tr"):
            row = [clean_text(td.get_text()) for td in tr.find_all("td")]
            if row:
                rows.append(row)

        if headers:
            parts.append(" | ".join(headers))
            parts.append(" | ".join(["---"] * len(headers)))
        for row in rows:
            parts.append(" | ".join(row))
        parts.append("\n")  # Separate tables from other content

    # Convert rest of the HTML (excluding tables) into readable format
    for el in soup.find_all(["h1", "h2", "h3", "p", "ul", "ol", "li", "pre", "code"]):
        if el.name in ["table", "tr", "td", "th"]:
            continue  # Already handled
        elif el.name.startswith("h"):
            level = int(el.name[1])
            parts.append(f"{'#' * level} {clean_text(el.get_text())}")
        elif el.name == "li":
            parts.append(f"- {clean_text(el.get_text())}")
        elif el.name in ("pre", "code"):
            code = el.get_text()
            parts.append(f"\n```\n{code.strip()}\n```\n")
        else:
            parts.append(clean_text(el.get_text()))

    return "\n\n".join(part for part in parts if part.strip())



async def load_html_docs(directory="data"):
    """Load HTML files and extract all readable documentation text."""
    try:
        logger.info(f"Loading HTML documents from {directory}")
        docs = []
        for filename in os.listdir(directory):
            if filename.endswith(".html"):
                path = os.path.join(directory, filename)
                async with aiofiles.open(path, encoding="utf-8") as f:
                    content = await f.read()
                    structured_text = extract_structured_text(content)
                    docs.append(structured_text)
                    logger.info(f"Processed {filename}")
        logger.info(f"Total documents loaded: {len(docs)}")
        return docs
    except Exception as e:
        logger.error(f"Error in load_html_docs: {e}", exc_info=True)
        raise


def chunk_text(text):
    """Token-based overlapping chunking."""
    try:
        tokens = tokenizer.encode(text)
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + CHUNK_SIZE, len(tokens))
            chunk = tokenizer.decode(tokens[start:end])
            chunks.append(chunk)
            if end == len(tokens):
                break
            start += CHUNK_SIZE - CHUNK_OVERLAP
        logger.info(f"Chunked into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.error(f"Error in chunk_text: {e}", exc_info=True)
        raise


def cosine_similarity(a, b):
    return 1 - cosine(a, b)

async def embed_texts(texts: list[str]):
    try:
        logger.info(f"Embedding {len(texts)} chunks")
        response = await client.embeddings.create(
            input=texts,
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        )
        embeddings = [e.embedding for e in response.data]
        logger.info("Embedding complete")
        return embeddings
    except Exception as e:
        logger.error(f"Error in embed_texts: {e}", exc_info=True)
        raise


async def prepare_doc_embeddings():
    """Load, chunk, embed and store all docs for retrieval."""
    global doc_chunks
    try:
        logger.info("Preparing document embeddings")
        docs = await load_html_docs()
        all_chunks = []
        for doc in docs:
            all_chunks.extend(chunk_text(doc))
        embeddings = await embed_texts(all_chunks)
        doc_chunks = list(zip(all_chunks, embeddings))
        logger.info(f"Prepared {len(doc_chunks)} embedded chunks")
    except Exception as e:
        logger.error(f"Error in prepare_doc_embeddings: {e}", exc_info=True)
        raise


async def retrieve_relevant_chunks(query: str, top_k=3):
    try:
        logger.info(f"Retrieving relevant chunks for: {query}")
        query_embedding = (await embed_texts([query]))[0]
        scored = [
            (text, cosine_similarity(np.array(query_embedding), np.array(embed)))
            for text, embed in doc_chunks
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_chunks = [text for text, score in scored[:top_k]]
        logger.info(f"Top {top_k} chunks returned")
        return top_chunks
    except Exception as e:
        logger.error(f"Error in retrieve_relevant_chunks: {e}", exc_info=True)
        raise
