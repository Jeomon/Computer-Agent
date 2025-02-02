from src.agent.terminal.utils import extract_agent_data,read_markdown_file
from src.message import AIMessage,HumanMessage,SystemMessage
from src.agent.terminal.registry import Registry
from langgraph.graph import StateGraph,START,END
from src.agent.terminal.tools import shell_tool
from src.agent.terminal.state import AgentState
from src.inference import BaseInference
from src.agent import BaseAgent
from termcolor import colored
from platform import platform
from datetime import datetime
from getpass import getuser
from src.tool import Tool
from pathlib import Path
from os import getcwd
import json

tools=[
    shell_tool
]

class TerminalAgent(BaseAgent):
    def __init__(self,instructions:list[str]=[],additional_tools:list[Tool]=[],llm:BaseInference=None,verbose:bool=False,max_iteration:int=10,token_usage:bool=False):
        """
        Initialize a Terminal Agent instance.

        Args:
            instructions (list[str], optional): A list of instructions for the agent to follow. Defaults to an empty list.
            additional_tools (list[Tool], optional): A list of additional tools to be used by the agent. Defaults to an empty list.
            llm (BaseInference, optional): The language model inference engine used by the agent. Defaults to None.
            verbose (bool, optional): Whether to enable verbose output to show the agent's flow. Defaults to False.
            max_iteration (int, optional): The maximum number of iterations the agent should perform. Defaults to 10.
            token_usage (bool, optional): Whether to track token usage. Defaults to False.
        """
        self.name='Terminal Agent'
        self.description='The Terminal Agent is an AI-powered automation tool designed to interact with the terminal or command line interface. It can execute shell commands, run scripts, and perform other terminal-based tasks.'
        self.llm=llm
        self.verbose=verbose
        self.max_iteration=max_iteration
        self.iteration=0
        self.instructions=self.format_instructions(instructions)
        self.registry=Registry(tools+additional_tools)
        self.system_prompt=read_markdown_file('./src/agent/terminal/prompt/system.md')
        self.human_prompt=read_markdown_file('./src/agent/terminal/prompt/human.md')
        self.ai_prompt=read_markdown_file('./src/agent/terminal/prompt/ai.md')
        self.graph=self.create_graph()
        self.token_usage=token_usage

    def format_instructions(self,instructions):
        return '\n'.join([f'{i+1}. {instruction}' for (i,instruction) in enumerate(instructions)])

    def reason(self,state:AgentState):
        llm_response=self.llm.invoke(state.get('messages'))
        # print(llm_response.content)
        agent_data=extract_agent_data(llm_response.content)
        # print(dumps(agent_data,indent=2))
        thought=agent_data.get('Thought')
        route=agent_data.get('Route')
        if self.verbose:
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        return {**state,'agent_data': agent_data,'route':route}

    def action(self,state:AgentState):
        agent_data=state.get('agent_data')
        thought=agent_data.get('Thought')
        action_name=agent_data.get('Action Name')
        action_input=agent_data.get('Action Input')
        route=agent_data.get('Route')
        if self.verbose:
            print(colored(f'Action Name: {action_name}',color='blue',attrs=['bold']))
            print(colored(f'Action Input: {action_input}',color='blue',attrs=['bold']))
        action_result=self.registry.execute(name=action_name,params=action_input)
        observation=action_result.content
        if self.verbose:
            print(colored(f'Observation: {observation}',color='green',attrs=['bold']))
        if self.verbose and self.token_usage:
            print(f'Input Tokens: {self.llm.tokens.input} Output Tokens: {self.llm.tokens.output} Total Tokens: {self.llm.tokens.total}')
        # Delete the last message
        state.get('messages').pop()
        ai_prompt=self.ai_prompt.format(thought=thought,action_name=action_name,action_input=json.dumps(action_input,indent=2),route=route)
        human_prompt=self.human_prompt.format(observation=observation)
        messages=[AIMessage(ai_prompt),HumanMessage(human_prompt)]
        return {**state,'agent_data':agent_data,'messages':messages}
    
    def final(self,state:AgentState):
        agent_data=state.get('agent_data')
        final_answer=agent_data.get('Final Answer')
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='cyan',attrs=['bold']))
        return {**state,'output':final_answer}

    def controller(self,state:AgentState):
        route=state.get('route')
        return route.lower()
        
    def create_graph(self):
        workflow=StateGraph(AgentState)
        workflow.add_node('reason',self.reason)
        workflow.add_node('action',self.action)
        workflow.add_node('final',self.final)

        workflow.add_edge(START,'reason')
        workflow.add_conditional_edges('reason',self.controller)
        workflow.add_edge('action','reason')
        workflow.add_edge('final',END)

        return workflow.compile(debug=False)

    def invoke(self,input:str):
        if self.verbose:
            print(f'Entering '+colored(self.name,'black','on_white'))
        parameters={
            'instructions':self.instructions,
            'current_datetime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'actions_prompt':self.registry.actions_prompt(),
            'os':platform(),
            'home_dir':Path.home().as_posix(),
            'user':getuser(),

        }
        system_prompt=self.system_prompt.format(**parameters)
        user_prompt=f'Task: {input}'
        state={
            'input':input,
            'messages':[SystemMessage(system_prompt),HumanMessage(user_prompt)],
            'agent_data':{},
            'output':''
        }
        graph_response=self.graph.invoke(state)
        return graph_response.get('output')

    def stream(self,input:str):
        pass
        