from pathlib import Path
from langchain_core.tools import tool
import pandas as pd 
from datetime import datetime
project_root=Path(__file__).resolve().parent.parent
from src.config import feedback_log_location

feedback_log = pd.read_csv(feedback_log_location)
@tool
def register_feedback(intent: str, customer_id: int, feedback: str, rating: int) -> str:
    """
    Logs customer feedback into the feedback log.

    Args:
        intent (str): The category of the support query (e.g., "cancel_order", "get_refund").
        customer_id (int): The unique ID of the customer.
        feedback (str): The feedback provided by the customer.
        rating(int): The rating provided by the customer out of 5

    Returns:
        str: Success message.
    """
    global feedback_log
    feedback_entry = {
        "timestamp": datetime.now(),
        "intent": intent,
        "customer_id": customer_id,
        "feedback": feedback,
        "rating": rating
    }
    feedback_log = pd.concat([feedback_log, pd.DataFrame([feedback_entry])], ignore_index=True)

    feedback_log.to_csv(feedback_log_location)
    return "Feedback registered successfully!"

