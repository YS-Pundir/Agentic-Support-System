from langchain_core.tools import tool
from datetime import datetime

@tool
def days_since(delivered_date: str) -> str:
    """
    Calculates the number of days since the product was delivered.

    Args:
        delivered_date (str): The date when the product was delivered in the format 'YYYY-MM-DD'.
    """
    try:
        # Convert the delivered_date string to a datetime object
        delivered_date = datetime.strptime(delivered_date, '%Y-%m-%d')
        today = datetime.today()

        # Calculate the difference in days
        days_difference = str((today - delivered_date).days)

        return days_difference
    except ValueError as e:
        return f"Error: {e}"

