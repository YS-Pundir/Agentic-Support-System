
import json
from pathlib import Path
project_root=Path(__file__).resolve().parent.parent
import os
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("api_key")

sql_config_path=project_root/"configs"/"sql_agent.json"
rag_config_path=project_root/"configs"/"rag_agent.json"

support_config_path=project_root/"configs"/"support_agent.json"
def settings(config_path:Path):
    with open(config_path, "r") as f:
        data=json.load(f)
    return data

def get_prompt(prompt_path:Path):
    with open(prompt_path, "r") as f:
        data=f.read()
    return data

rag_data=settings(rag_config_path)
rag_model=rag_data["rag_agent"]["v1"]["config"]["model"]
rag_prompt_path=rag_data["rag_agent"]["v1"]["prompt_path"]
rag_prompt=get_prompt(rag_prompt_path)
rag_temperature=rag_data["rag_agent"]["v1"]["config"]["temperature"]

sql_data=settings(sql_config_path)
sql_model=sql_data["sql_agent"]["v1"]["config"]["model"]
sql_prompt_path=sql_data["sql_agent"]["v1"]["prompt_path"]
sql_prompt=get_prompt(sql_prompt_path)
sql_temperature=sql_data["sql_agent"]["v1"]["config"]["temperature"]


support_data=settings(support_config_path)
support_model=support_data["support_agent"]["v1"]["config"]["model"]
support_prompt_path=support_data["support_agent"]["v1"]["prompt_path"]
support_prompt=get_prompt(support_prompt_path)
support_temperature=support_data["support_agent"]["v1"]["config"]["temperature"]
support_tools=support_data["support_agent"]["v1"]["tools"]

persisted_vectordb_location = project_root/"Database"/"policy_docs"
db_loc = project_root/'Database'/'ecomm.db'

rag_log_location=project_root/"log"/"rag_tool.log"
sql_log_location=project_root/"log"/"sql_agent.log"
support_log_location=project_root/"log"/"support_agent.log"

feedback_log_location=project_root/"Storage"/"agent_feedbacks.csv"
deferred_case_location=project_root/"Storage"/"deffered_cases.csv"

conversation_history_location=project_root/"Storage"/"support_agent_conversation.json"
