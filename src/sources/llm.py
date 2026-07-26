from langchain_groq import ChatGroq
from src.config import api_key
from src.config import rag_temperature,rag_model
from src.config import sql_temperature,sql_model
from src.config import support_temperature,support_model




sql_llm=ChatGroq(
    model=sql_model,
    temperature=sql_temperature,
    api_key=api_key 
)

support_llm=ChatGroq(
    model=support_model,
    temperature=support_temperature,
    api_key=api_key 
)


