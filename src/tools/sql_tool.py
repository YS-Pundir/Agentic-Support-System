
import pandas as pd
import numpy as np
import json


from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from src.config import sql_log_location,db_loc
from src.config import api_key
from src.config import sql_model,sql_prompt,sql_temperature
from src.sources.llm import sql_llm


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
    filename=sql_log_location,
    filemode="a",

)

logger = logging.getLogger(__name__)
attempt_counter={"n":0}



# Create a SQLDatabase instance from the SQLite database URI
db = SQLDatabase.from_uri(f"sqlite:///{db_loc}")

# Retrieve the schema information of the database tables
database_schema = db.get_table_info()

full_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", sql_prompt),
        ("human", '{input}'),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)



# Create the SQL agent using the AzureChatOpenAI model, database, and prompt template
sqlite_agent = create_sql_agent(
    llm=sql_llm,
    db=db,
    prompt=full_prompt,
    agent_type="openai-tools",
    agent_executor_kwargs={'handle_parsing_errors': True},
    max_iterations=5,
    verbose=True
)



@tool
@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1,min=1,max=10),
    before_sleep=before_sleep_log(logger,logging.WARNING)
)
def sql_tool(user_input: str) -> str:
    """
    Executes a SQL query using the sqlite_agent and returns the result.

    Args:
        user_input (str): a natural language query string explaining what information is required while also providing the necessary details to get the information.

    Returns:
        str: The result of the SQL query execution. If an error occurs, the exception is returned as a string.
    """
    try:
        # Invoke the sqlite_agent with the user input (SQL query)
        response = sqlite_agent.invoke(user_input)

        # Extract the output from the response
        prediction = response['output']

    except Exception as e:
        # If an exception occurs, capture the exception message
        prediction = e

    # Return the result or the exception message
    return prediction
