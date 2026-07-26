
import json
from datetime import datetime
from src.config import api_key
from src.config import persisted_vectordb_location
from src.config import rag_log_location

from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_classic.vectorstores import Chroma
from langchain_core.tools import tool

from src.config import rag_model,rag_prompt,rag_temperature
qna_system_message=rag_prompt
from groq import Groq
client=Groq(api_key=api_key)

# For Api Rate limiting
import logging
from tenacity import (
     retry,  # Decorator that wraps a function with retry logic
    stop_after_attempt,  # Stop after N total attempts
    wait_exponential,  # Wait 1s, 2s, 4s, 8s between retries
    before_sleep_log, 

)



logging.basicConfig(
    level=logging.INFO,
    filename=rag_log_location,
    filemode="a",
)

logger = logging.getLogger(__name__)
attempt_counter={"n":0}




# Initialise the embedding model
embedding_model = SentenceTransformerEmbeddings(model_name='thenlper/gte-large')

# Load the persisted DB

#Create a Colelction Name
collection_name = 'policy_docs'
# Load the persisted DB
vector_store = Chroma(
    collection_name=collection_name,
    persist_directory=str(persisted_vectordb_location),
    embedding_function=embedding_model

)


qna_user_message_template = """
###Context
Here are some documents and their source that may be relevant to the question mentioned below.
{context}

###Question
{question}
"""



retriever = vector_store.as_retriever(
    search_type='similarity',
    search_kwargs={'k': 5}
)

@tool
@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1,min=1,max=10),
    before_sleep=before_sleep_log(logger,logging.WARNING)
)
def rag(user_input: str) -> str:

    """
    Search the company knowledge base.

    Use this tool whenever the user asks about:

    - refund policy
    - cancellation policy
    - warranty
    - shipping policy
    - return policy
    - invoice policy
    - product information
    - FAQs
    - company policies

    Do NOT use this tool for order lookup, tracking, or customer information.

    Args:
        user_input: The user's complete question.

    Returns:
        Answer from the company knowledge base.

    """

    relevant_document_chunks = retriever.invoke(user_input)
    context_list = [d.page_content + "\n ###Source: " + d.metadata['source'] + "\n\n " for d in relevant_document_chunks]

    context_for_query = ". ".join(context_list)
    # print("context: ", context_for_query)  # Use this to understand what context is provided BTS and to debug.
    prompt = [
        {'role':'system', 'content': qna_system_message},
        {'role': 'user', 'content': qna_user_message_template.format(
            context=context_for_query,
            question=user_input
            )
        }
    ]

    try:
        response = client.chat.completions.create(
        model=rag_model,
        messages=prompt
        )

        prediction = response.choices[0].message.content
    except Exception as e:
        prediction = f'Sorry, I encountered the following error: \n {e}'

    return prediction




