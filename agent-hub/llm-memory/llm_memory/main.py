import json
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
import os
from dotenv import load_dotenv
from mofa.kernel.base import MemoryAgent
from openai import OpenAI
from mofa.utils.files.read import read_yaml
from mem0 import Memory
@run_agent
def run(agent: MofaAgent,memory,messages:list=[]):
    query = agent.receive_parameter(parameter_name='query')
    os.environ['OPENAI_API_KEY'] = os.getenv('LLM_API_KEY')

    user_id = os.getenv('MEMORY_ID', 'mofa-memory-user')

    relevant_memories = memory.search(query=query, user_id=user_id, limit=os.getenv('MEMORY_LIMIT', 5))
    print('relevant_memories : ',relevant_memories)
    base_url = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1')

    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=base_url)
    response = client.chat.completions.create(
        # model="deepseek-chat",
        model=os.getenv('LLM_MODEL_NAME', 'gpt-4o'),
        messages=[
            {"role": "system", "content": os.getenv('SYSTEM_PROMPT',
                                                    'You are a helpful assistant that helps people find information.') + f'   Memory Data {relevant_memories}'},
            {"role": "user", "content": f"user query: {query}  "},
        ],
        stream=False
    )
    messages.append({'role': 'user', 'content': query})
    messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
    memory.add_messages(messages=messages, user_id=user_id)
    agent.send_output(agent_output_name='llm-memory-result', agent_result=response.choices[0].message.content)


def main():
    config_path = 'llm_config.yaml'
    load_dotenv('.env')
    api_key = os.getenv('LLM_API_KEY')
    os.environ['OPENAI_API_KEY'] = api_key

    try:
        agent = MofaAgent(agent_name='LLM-Memory-Agent')
        memory = MemoryAgent(config_path)
        run(agent,memory=memory)
    except Exception as e:
        print(f'Error initializing MemoryAgent: {e}')



if __name__ == "__main__":
    main()
