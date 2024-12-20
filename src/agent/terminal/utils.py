import re

def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r',encoding='utf-8') as f:
        markdown_content = f.read()
    return markdown_content

def extract_llm_response(text):
    # Dictionary to store extracted values
    result = {}
    # Check if it's Option 1 (Command-based)
    if re.search(r"<Command>", text):
        # Extract Thought
        thought_match = re.search(r"<Thought>(.*?)<\/Thought>", text, re.DOTALL)
        if thought_match:
            result['Thought'] = thought_match.group(1).strip()
        # Extract Command
        command_match = re.search(r"<Command>(.*?)<\/Command>", text, re.DOTALL)
        if command_match:
            result['Command'] = command_match.group(1).strip()
        # Extract Route (should always be 'Command' in Option 1)
        route_match = re.search(r"<Route>(.*?)<\/Route>", text, re.DOTALL)
        if route_match:
            result['Route'] = route_match.group(1).strip()
            
    # Check if it's Option 2 (Final Answer)
    elif re.search(r"<Final-Answer>", text):
        # Extract Thought
        thought_match = re.search(r"<Thought>(.*?)<\/Thought>", text, re.DOTALL)
        if thought_match:
            result['Thought'] = thought_match.group(1).strip()
        # Extract Final Answer
        final_answer_match = re.search(r"<Final-Answer>(.*?)<\/Final-Answer>", text, re.DOTALL)
        if final_answer_match:
            result['Final Answer'] = final_answer_match.group(1).strip()
        # Extract Route (should always be 'Final' in Option 2)
        route_match = re.search(r"<Route>(.*?)<\/Route>", text, re.DOTALL)
        if route_match:
            result['Route'] = route_match.group(1).strip()
        # Extract Plan from Option 2
        plan_match = re.search(r"<Plan>(.*?)<\/Plan>", text, re.DOTALL)
        if plan_match:
            result['Plan'] = plan_match.group(1).strip()

    # Check if it's Option 3 (Retrieving Information from Memory)
    elif re.search(r"<Agent>", text):
        # Extract Thought
        thought_match = re.search(r"<Thought>(.*?)<\/Thought>", text, re.DOTALL)
        if thought_match:
            result['Thought'] = thought_match.group(1).strip()

        # Extract Agent
        agent_match = re.search(r"<Agent>(.*?)<\/Agent>", text, re.DOTALL)
        if agent_match:
            result['Agent'] = agent_match.group(1).strip()

        # Extract Request (the specific information being requested)
        request_match = re.search(r"<Request>(.*?)<\/Request>", text, re.DOTALL)
        if request_match:
            result['Request'] = request_match.group(1).strip()

        # Extract Route (should always be 'Retrieve' in Option 3)
        route_match = re.search(r"<Route>(.*?)<\/Route>", text, re.DOTALL)
        if route_match:
            result['Route'] = route_match.group(1).strip()
    return result
