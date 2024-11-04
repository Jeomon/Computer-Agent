from typing import TypedDict,Annotated
from src.message import BaseMessage
from operator import add

class AgentState(TypedDict):
    input:str
    agent_data:dict
    bboxes:list[dict]
    output:str
    previous_observation:str
    messages:Annotated[list[BaseMessage],add]