from src.sources.llm import support_llm

from src.config import support_prompt,conversation_history_location,support_log_location
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
import json

from src.tools.rag_tool import rag
from src.tools.sql_tool import sql_tool
from src.tools.daycount_tool import days_since
from src.tools.feedback_tool import register_feedback
from src.tools.deffered_tool import defer_to_human
tools=[rag,sql_tool,days_since,register_feedback,defer_to_human]


max_messages=3


# For Api Rate limiting
import logging
from tenacity import (
     retry,  # Decorator that wraps a function with retry logic
    stop_after_attempt,  # Stop after N total attempts
    wait_exponential,  # Wait 1s, 2s, 4s, 8s between retries
    before_sleep_log, 

)

# 2. Clear out any existing handlers so Python doesn't write to the old file
for handler in logging.root.handlers[:]:
  logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    filename=support_log_location,
    filemode="a",

)

logger = logging.getLogger(__name__)
attempt_counter={"n":0}




full_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", support_prompt),
        ("human", '{input}'),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)




agent = create_tool_calling_agent(support_llm, tools, full_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Function to process user input and generate a chatbot response
# Function to process user input and generate a chatbot response
@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1,min=1,max=10),
    before_sleep=before_sleep_log(logger,logging.WARNING)
)
def chat_with_agent():
    print("Chatbot is ready! Type 'exit' to end the conversation.")
    conversation_history = [{"role": "assistant", "content": "Hey, how can I help you?"}]

    # Display the initial greeting
    print("Chatbot: Hey, how can I help you?")

    while True:
        # Get user input
        user_input = input("You: ")

        # Exit condition
        if user_input.lower() == "exit":
            print("Chatbot: Thank you for chatting. Goodbye!")
            break

        # Add user input to conversation history
        conversation_history.append({"role": "user", "content": user_input})

        conversation_input = "\n".join(
            [f"{turn['role'].capitalize()}: {turn['content']}" for turn in conversation_history]
        )
        # Pass the history to the agent
        response = agent_executor.invoke({"input": conversation_input})

        # Add the chatbot's response to the history
        chatbot_response = response['output']
        conversation_history.append({"role": "assistant", "content": chatbot_response})
        with open(conversation_history_location,"a") as f:
            json.dump(conversation_history,f,indent=4)

        # Display the chatbot's response
        print(f"Chatbot: {chatbot_response}")
