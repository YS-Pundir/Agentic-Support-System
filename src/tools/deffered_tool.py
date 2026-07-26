
from datetime import datetime
import pandas as pd
from langchain.tools import tool
from src.config import deferred_case_location

deferred_cases = pd.read_csv(deferred_case_location)

@tool
def defer_to_human(customer_id: str, query: str, intent: str, reason: str) -> str:
    """
    Logs customer details and the reason for deferring to a human agent.

    Args:
        customer_id (int): The unique ID of the customer whose query is being deferred.
        query (str): The customer's query or issue that needs human intervention.
        intent (str): The category of the support query (e.g., "order_tracking", "product_description",...etc)
        reason (str): The reason why the query cannot be resolved by the chatbot.

    Returns:
        str: Success message indicating the deferral was logged.
    """
    global deferred_cases
    case_entry = {
        "timestamp": datetime.now(),
        "customer_id": customer_id,
        "query": query,
        "reason": reason,
        "intent": intent
    }
    deferred_cases = pd.concat([deferred_cases, pd.DataFrame([case_entry])], ignore_index=True)
    deferred_cases.to_csv(deferred_case_location, index=False)
    print("defer_to_human success")
    return "Case deferred to human agent and logged successfully!"

