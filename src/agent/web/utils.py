import re
import ast

def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    return markdown_content

def extract_llm_response(text):
    # Dictionary to store extracted values
    result = {}

    # Check if it's Option 1 (Action-based)
    if re.search(r"<Action-Name>", text):
        # Extract Thought
        thought_match = re.search(r"<Thought>(.*?)<\/Thought>", text, re.DOTALL)
        if thought_match:
            result['Thought'] = thought_match.group(1).strip()

        # Extract Action-Name
        action_name_match = re.search(r"<Action-Name>(.*?)<\/Action-Name>", text, re.DOTALL)
        if action_name_match:
            result['Action Name'] = action_name_match.group(1).strip()

        # Extract and convert Action-Input to a dictionary
        action_input_match = re.search(r"<Action-Input>(.*?)<\/Action-Input>", text, re.DOTALL)
        if action_input_match:
            action_input_str = action_input_match.group(1).strip()
            try:
                # Convert string to dictionary safely using ast.literal_eval
                result['Action Input'] = ast.literal_eval(action_input_str)
            except (ValueError, SyntaxError):
                # If there's an issue with conversion, store it as raw string
                result['Action Input'] = action_input_str

        # Extract Route (should always be 'Action' in Option 1)
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
