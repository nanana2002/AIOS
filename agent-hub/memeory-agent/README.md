# Memory Agent Node

A MOFA node that provides comprehensive memory management capabilities using Mem0 AI, combining both memory retrieval and storage operations. This node acts as a memory orchestrator that can search existing memories, store new conversations, and manage the complete memory lifecycle for AI applications.

## Features

- **Memory Search and Retrieval**: Query existing memories using semantic search
- **Memory Storage**: Store new conversation messages and context
- **Dual-Phase Operation**: Combines retrieval and storage in a single workflow
- **User-Specific Memory**: Maintains separate memory spaces for different users
- **Configurable Memory Limits**: Control the number of retrieved memories
- **Real-time Memory Updates**: Dynamic memory updates during conversation flow

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

### Environment Configuration (`.env.secret`)
Required environment variables:

```bash
# OpenAI API Configuration
LLM_API_KEY=your_openai_api_key_here

# Memory Configuration (Optional)
MEMORY_ID=mofa-memory-user  # Default user ID for memory operations
MEMORY_LIMIT=5             # Number of memories to retrieve per search
```

### Memory Configuration (`configs/config.yml`)
Configure the memory system:

```yaml
system: null
agent:
  llm:
    provider: openai
    config:
      model: "gpt-4o"
      max_tokens: 3200

  vector_store:
    provider: chroma
    config:
      collection_name: "mofa-memory"
      path: "db"

  embedder:
    provider: openai
    config:
      model: "text-embedding-3-large"

  user_id: "mofa"
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Query to search for relevant memories |
| `agent_result` | string | Yes | LLM response to be stored in memory |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `memory_retrieval_result` | string (JSON) | Retrieved relevant memories based on query |
| `memory_record_result` | string (JSON) | Confirmation of memory storage operation |

## Usage Example

### Basic Dataflow Configuration

This node is typically used in a memory-augmented conversation flow:

```yaml
# mem0_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      memory_retrieval_result: memory-agent/memory_retrieval_result
      reasoner_result: reasoner/reasoner_result
      memory_record_result: memory-agent/memory_record_result

  - id: memory-agent
    build: pip install -e ../../agent-hub/memeory-agent
    path: memeory-agent
    outputs:
      - memory_retrieval_result
      - memory_record_result
    inputs:
      query: terminal-input/data
      agent_result: reasoner/reasoner_result

  - id: reasoner
    build: pip install -e ../../agent-hub/memory-reasoner
    path: memory-reasoner
    inputs:
      task: terminal-input/data
      memory_context: memory-agent/memory_retrieval_result
    outputs:
      - reasoner_result
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "LLM_API_KEY=your_openai_api_key" > .env.secret
   echo "MEMORY_ID=user123" >> .env.secret
   echo "MEMORY_LIMIT=5" >> .env.secret
   ```

2. **Start the MOFA framework:**
   ```bash
   dora up
   ```

3. **Build and start the dataflow:**
   ```bash
   dora build mem0_dataflow.yml
   dora start mem0_dataflow.yml
   ```

4. **The system will:**
   - Search memories based on user queries
   - Provide memory context to reasoning agents
   - Store new conversation results back to memory

## Code Example

The core functionality is implemented in `main.py`:

```python
import json
import os
from dotenv import load_dotenv
from mofa.agent_build.base.base_agent import run_agent, MofaAgent
from mem0 import Memory
from mofa.utils.files.read import read_yaml

@run_agent
def run(agent: MofaAgent, memory: Memory, user_id: str = None, messages: list = None):
    
    if user_id is None:
        user_id = os.getenv('MEMORY_ID', 'mofa-memory-user')
    
    # Phase 1: Memory Retrieval
    query = agent.receive_parameter('query')
    relevant_memories = memory.search(
        query=query, 
        user_id=user_id, 
        limit=os.getenv('MEMORY_LIMIT', 5)
    )
    
    print('----relevant_memories------:', relevant_memories)
    
    # Format memories for output
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
    agent.send_output(
        'memory_retrieval_result', 
        agent_result=json.dumps(memories_str),
        is_end_status=False
    )
    
    # Phase 2: Wait for LLM Response and Store
    llm_result = agent.receive_parameter('agent_result')
    
    # Create conversation messages
    messages.append({'role': 'user', 'content': query})
    messages.append({'role': 'assistant', 'content': llm_result})
    
    print('------', messages)
    
    # Store new conversation in memory
    memory.add(messages, user_id=user_id)
    print('all result:', memory.get_all(user_id=user_id))
    
    # Send storage confirmation
    agent.send_output(
        'memory_record_result', 
        agent_result=json.dumps('Add Memory Success'),
        is_end_status=True
    )

def main():
    agent = MofaAgent(agent_name='memory-agent')
    load_dotenv('.env.secret')
    
    # Load memory configuration
    config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), ) + '/configs/config.yml'
    config_data = read_yaml(str(config_path))
    
    # Set up OpenAI API key
    os.environ['OPENAI_API_KEY'] = os.getenv('LLM_API_KEY')
    
    # Initialize memory system
    memory = Memory.from_config(config_data.get('agent'))
    
    # Run the agent
    run(agent=agent, memory=memory, messages=[])
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **mem0ai** (>= 0.1.97): For comprehensive memory management capabilities
- **flask**: For web server capabilities
- **python-dotenv**: For environment variable management (needs to be added to pyproject.toml)
- **mofa**: MOFA framework (automatically available in MOFA environment)

**Note**: This node requires `python-dotenv` which should be added to `pyproject.toml`.

## Key Features

### Dual-Phase Memory Operation

#### Phase 1: Memory Retrieval
- Receives user query
- Searches existing memories using semantic similarity
- Returns formatted relevant memories
- Provides memory context to downstream agents

#### Phase 2: Memory Storage
- Receives processed LLM response
- Creates structured conversation messages
- Stores complete conversation in memory
- Confirms successful storage operation

### Memory Search Capabilities
- **Semantic Search**: Uses vector embeddings for intelligent memory retrieval
- **Relevance Ranking**: Returns most relevant memories first
- **Configurable Limits**: Control number of memories retrieved
- **User Context**: Maintains user-specific memory contexts

### Memory Storage Features
- **Conversation Threading**: Preserves complete conversation flows
- **Role-based Messages**: Structures messages with user/assistant roles
- **Persistent Storage**: Uses ChromaDB for reliable data persistence
- **Memory Growth**: Continuously builds memory over time

## Architecture Overview

### Memory Workflow
```
User Query ’ Memory Search ’ Context Retrieval ’ LLM Processing ’ Response Storage
     “              “              “                “              “
   Input         Semantic       Memory         AI Agent      Memory Update
  Parameter      Matching      Context        Processing      & Storage
```

### Integration Pattern
```yaml
Terminal Input ’ Memory Agent (Search) ’ Reasoner ’ Memory Agent (Store) ’ Output
                      “                      ‘              “
                Memory Context          Memory Context   Updated Memory
```

## Use Cases

### Conversational AI Systems
- **Context Preservation**: Maintain conversation history across multiple sessions
- **Personalized Responses**: Use past interactions to personalize AI responses
- **Learning Systems**: Enable AI to learn from user preferences and feedback
- **Multi-turn Conversations**: Support complex, context-aware dialogues

### Customer Support Applications
- **Case History**: Maintain complete customer interaction history
- **Context Transfer**: Preserve context when conversations are transferred between agents
- **Issue Tracking**: Remember previous issues and their resolutions
- **Customer Insights**: Build comprehensive customer profiles over time

### Educational and Training Systems
- **Learning Progress**: Track student learning patterns and progress
- **Adaptive Content**: Adjust content based on past learning interactions
- **Performance Monitoring**: Monitor and store learning outcomes
- **Personalized Tutoring**: Provide personalized educational experiences

## Advanced Configuration

### Memory Search Optimization
```bash
# Fine-tune memory retrieval
MEMORY_LIMIT=10        # Increase retrieved memories
MEMORY_THRESHOLD=0.7   # Similarity threshold for retrieval
MEMORY_DECAY=0.95      # Time-based memory importance decay
```

### Multi-User Memory Management
```python
def handle_multiple_users():
    users = {
        'user1': 'project_alpha_context',
        'user2': 'customer_support_context', 
        'user3': 'educational_context'
    }
    
    for user_id, context in users.items():
        memories = memory.search(query=query, user_id=user_id, limit=5)
        # Process memories for each user context
```

### Memory Performance Tuning
```yaml
agent:
  vector_store:
    provider: chroma
    config:
      collection_name: "high-performance-memory"
      path: "optimized_db"
      distance_function: "cosine"
      
  embedder:
    provider: openai
    config:
      model: "text-embedding-3-large"
      batch_size: 100
```

## Integration with Other Agents

### Memory-Reasoner Pipeline
The node works closely with memory-reasoner agents:

1. **Memory Retrieval**: Provides relevant context to reasoner
2. **Reasoning Process**: Reasoner processes query with memory context
3. **Memory Storage**: Stores reasoner output for future reference

### Multi-Agent Memory Sharing
```python
# Shared memory across multiple agents
class SharedMemoryAgent(MofaAgent):
    def __init__(self, shared_memory_config):
        self.memory = Memory.from_config(shared_memory_config)
        # Multiple agents can access the same memory instance
```

## Performance Optimization

### Memory Efficiency
- **Smart Retrieval**: Optimize search queries to retrieve most relevant memories
- **Memory Pruning**: Implement periodic cleanup of outdated memories
- **Batch Operations**: Group memory operations for better performance
- **Caching**: Cache frequently accessed memories

### Storage Optimization
- **Vector Compression**: Use appropriate embedding dimensions
- **Database Tuning**: Optimize ChromaDB configuration
- **Memory Limits**: Implement memory growth limits
- **Archival Strategies**: Archive old memories to maintain performance

## Troubleshooting

### Common Issues
1. **Memory Search Returns Empty**: Check user_id consistency and memory initialization
2. **Storage Failures**: Verify ChromaDB path and write permissions
3. **API Errors**: Confirm OpenAI API key and quota availability
4. **Configuration Errors**: Validate YAML configuration file syntax

### Debug Tips
- Monitor memory search results and storage confirmations
- Check ChromaDB database files and storage paths
- Verify user_id consistency across operations
- Test memory operations with simple queries first
- Enable detailed logging for memory operations

## Data Management

### Memory Lifecycle
- **Creation**: New memories created from conversations
- **Retrieval**: Existing memories retrieved based on queries
- **Updates**: Memories updated with new information
- **Archival**: Old memories archived or removed

### Data Privacy
- **User Isolation**: Memories strictly separated by user_id
- **Data Encryption**: Consider encryption for sensitive memory data
- **Access Control**: Implement proper access controls for memory data
- **Retention Policies**: Define clear data retention policies

## Contributing

1. Test with various memory scenarios and user patterns
2. Optimize memory search and storage algorithms
3. Add support for additional memory providers
4. Enhance memory lifecycle management features

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://mofa.ai/)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Mem0 AI](https://github.com/mem0ai/mem0)
- [Mem0 Documentation](https://docs.mem0.ai/)