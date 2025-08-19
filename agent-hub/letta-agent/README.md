
# Letta Agent Node

A MOFA node that provides persistent memory-enabled AI agent capabilities using Letta (formerly MemGPT). This node specializes in maintaining long-term memory of interactions while processing tasks, making it ideal for applications requiring conversational continuity and context retention across sessions.

## Features

- **Persistent Memory Management**: Uses Letta's advanced memory system for long-term interaction storage
- **Archival Memory Integration**: Stores and retrieves contextual information from past conversations
- **Configurable Agent Personas**: Customizable agent personality and human user profiles
- **Dynamic Task Processing**: Real-time task processing with memory-enhanced responses
- **LLM Integration**: Compatible with various LLM providers through Letta's configuration system
- **Embedding-Based Retrieval**: Uses embedding models for semantic memory search

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

### Environment Configuration (`.env.secret`)
Required environment variables:

```bash
# LLM Configuration
LLM_API_KEY=your_openai_api_key_here
LLM_MODEL_NAME=gpt-4o
LLM_EMBEDDER_MODEL_NAME=text-embedding-3-small

# Optional Configuration
TASK=default_task_description  # Optional default task
IS_DATAFLOW_END=true          # Dataflow end flag
```

### Agent Configuration (`configs/config.yml`)
Configure the agent's memory and persona:

```yaml
system: null
agent:
  user_id: mofa_letta
  memory:
    persona: You are a helpful assistant that remembers past interactions
    human: My name is mofa
  user:
    prompt: Hello! I'm here to assist you with any problem or task you're facing. I utilize my memory of previous interactions and a comprehensive knowledge base to provide tailored and effective solutions.
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task` | string | Yes | The task or query to process with memory context |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `letta_agent_result` | string | Memory-enhanced response to the task with stored context |

## Usage Example

### Basic Dataflow Configuration

```yaml
# letta_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      letta_agent_result: letta-agent/letta_agent_result

  - id: letta-agent
    build: pip install -e ../../agent-hub/letta-agent
    path: letta-agent
    outputs:
      - letta_agent_result
    inputs:
      task: terminal-input/data
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "LLM_API_KEY=your_openai_api_key" > .env.secret
   echo "LLM_MODEL_NAME=gpt-4o" >> .env.secret
   echo "LLM_EMBEDDER_MODEL_NAME=text-embedding-3-small" >> .env.secret
   ```

2. **Configure agent settings:**
   Edit `configs/config.yml` to customize the agent's persona and memory settings.

3. **Start the MOFA framework:**
   ```bash
   dora up
   ```

4. **Build and start the dataflow:**
   ```bash
   dora build letta_dataflow.yml
   dora start letta_dataflow.yml
   ```

5. **Send tasks to the agent:**
   Examples:
   - "Remember that I like coffee in the morning"
   - "What was my preference for morning beverages?"
   - "Help me plan a project based on our previous discussions"

## Code Example

The core functionality is implemented in `main.py`:

```python
from letta import create_client, LLMConfig, EmbeddingConfig
from letta.schemas.memory import ChatMemory
from mofa.agent_build.base.base_agent import BaseMofaAgent

class LettaAgent(BaseMofaAgent):
    def create_llm_client(self, config: dict = None, *args, **kwargs):
        self.init_llm_config()
        llm_config = self.load_config()
        
        # Set up OpenAI API key
        os.environ["OPENAI_API_KEY"] = os.environ.get('LLM_API_KEY')
        
        # Create Letta client
        self.llm_client = create_client()
        
        # Create agent with memory configuration
        self.agent_state = self.llm_client.create_agent(
            memory=ChatMemory(
                persona=llm_config.get('agent').get('memory').get('persona'),
                human=llm_config.get('agent').get('memory').get('human')
            ),
            llm_config=LLMConfig.default_config(
                model_name=os.environ.get('LLM_MODEL_NAME')
            ),
            embedding_config=EmbeddingConfig.default_config(
                model_name=os.environ.get('LLM_EMBEDDER_MODEL_NAME')
            )
        )

    def send_message_to_agent(self, prompt: str):
        response = self.llm_client.send_message(
            agent_id=self.agent_state_id,
            role="user",
            message=prompt
        )
        
        for message in response.messages:
            if message.message_type == 'tool_call_message':
                tool_call_args = json.loads(message.tool_call.arguments)
                return tool_call_args.get('message')

    def run(self, task: str = None, *args, **kwargs):
        # Retrieve existing memories
        memory_data = self.search_memory
        if len(memory_data) > 0:
            memory_context = 'These are the context memories: ' + '\n'.join(memory_data)
        else:
            memory_context = ''
        
        # Process task with memory context
        user_message = f"User task: {task}. Memory data: {memory_context}"
        agent_result = self.send_message_to_agent(prompt=user_message)
        
        # Record new memory
        self.record_memory(data=f'task: {task} agent result: {agent_result}')
        
        return agent_result
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **letta**: For memory-enabled AI agent capabilities
- **attrs**: For class definition and field management (needs to be added to pyproject.toml)
- **python-dotenv**: For environment variable management (needs to be added to pyproject.toml)
- **mofa**: MOFA framework (automatically available in MOFA environment)

**Note**: This node requires `attrs` and `python-dotenv` which should be added to `pyproject.toml`.

## Key Features

### Memory Management
- **Archival Memory**: Long-term storage and retrieval of conversation history
- **Contextual Recall**: Semantic search through past interactions
- **Memory Recording**: Automatic storage of tasks and responses
- **Memory Search**: Efficient retrieval of relevant historical context

### Agent Configuration
- **Custom Personas**: Configurable agent personality and behavior
- **User Profiles**: Customizable human user characteristics
- **Memory Initialization**: Configurable starting memory state
- **Flexible Settings**: YAML-based configuration management

### LLM Integration
- **Multiple Providers**: Support for various LLM providers through Letta
- **Embedding Models**: Configurable embedding models for memory operations
- **Model Flexibility**: Easy switching between different model configurations
- **API Management**: Secure API key handling and configuration

## Memory System

### Archival Memory
Letta's archival memory system provides:
- **Semantic Storage**: Contextual information stored with semantic meaning
- **Efficient Retrieval**: Fast lookup of relevant past information
- **Persistent Storage**: Memory persists across agent sessions
- **Scalable Architecture**: Handles large amounts of historical data

### Memory Operations
```python
# Search existing memories
memory_data = agent.search_memory

# Add new memory
agent.add_memory("Important information to remember")

# Record task and result
agent.record_memory(f"task: {task} result: {result}")
```

## Use Cases

### Conversational AI
- **Customer Support**: Maintain context across multiple support interactions
- **Personal Assistants**: Remember user preferences and history
- **Educational Tutors**: Track learning progress and adapt teaching methods
- **Therapy Bots**: Maintain therapeutic relationship continuity

### Task Management
- **Project Assistance**: Remember project details and progress across sessions
- **Research Support**: Maintain context of ongoing research topics
- **Writing Assistance**: Remember writing style and project requirements
- **Planning Tools**: Keep track of goals and progress over time

### Knowledge Management
- **Expert Systems**: Build expertise over time through interaction history
- **Documentation Assistants**: Remember organizational knowledge and procedures
- **Training Systems**: Track learner progress and adapt content accordingly
- **Advisory Services**: Maintain client relationship history and preferences

## Advanced Configuration

### Memory Persona Customization
```yaml
agent:
  memory:
    persona: |
      You are a specialized technical assistant with expertise in software development.
      You remember coding preferences, project details, and technical discussions
      to provide increasingly personalized and effective assistance.
    human: |
      I am a senior software engineer working on distributed systems.
      I prefer Python and have experience with microservices architecture.
```

### LLM Model Configuration
```bash
# High-performance configuration
LLM_MODEL_NAME=gpt-4o
LLM_EMBEDDER_MODEL_NAME=text-embedding-3-large

# Cost-optimized configuration  
LLM_MODEL_NAME=gpt-3.5-turbo
LLM_EMBEDDER_MODEL_NAME=text-embedding-3-small
```

## Integration Patterns

### With Other MOFA Agents
- **Multi-Agent Systems**: Share context between different specialized agents
- **Workflow Orchestration**: Maintain state across complex multi-step processes
- **Context Handoff**: Transfer relevant memory between different agent types
- **Collaborative Processing**: Multiple agents working on shared long-term projects

### Session Management
- **User Sessions**: Maintain separate memory spaces for different users
- **Project Contexts**: Isolate memories for different projects or domains
- **Temporal Organization**: Organize memories by time periods or project phases
- **Access Control**: Manage memory access permissions and privacy

## Troubleshooting

### Common Issues
1. **Memory Not Persisting**: Check Letta client configuration and storage setup
2. **API Key Errors**: Verify LLM and embedding model API keys
3. **Model Loading Issues**: Ensure model names are correctly specified
4. **Memory Search Empty**: Check if memories are being recorded properly

### Debug Tips
- Monitor memory storage and retrieval operations
- Check Letta client initialization and agent state
- Verify environment variable configuration
- Test memory operations independently
- Enable detailed logging for debugging

## Performance Optimization

### Memory Efficiency
- **Memory Pruning**: Regular cleanup of irrelevant or outdated memories
- **Selective Storage**: Store only important information to reduce memory bloat
- **Compression**: Use summarization techniques for large memory chunks
- **Indexing**: Optimize memory search with proper indexing strategies

### Response Performance
- **Model Selection**: Balance model capability with response speed
- **Memory Limits**: Set appropriate limits on memory retrieval
- **Caching**: Cache frequently accessed memories
- **Batching**: Process multiple related tasks efficiently

## Contributing

1. Test with various conversation patterns and memory scenarios
2. Enhance memory organization and retrieval algorithms
3. Add support for additional LLM providers and models
4. Improve integration with other memory management systems

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://mofa.ai/)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Letta (formerly MemGPT)](https://github.com/cpacker/MemGPT)
- [Letta Documentation](https://docs.letta.com/)
