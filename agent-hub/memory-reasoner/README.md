# Memory Reasoner Node

A MOFA node that provides intelligent reasoning capabilities with memory context integration. This node specializes in processing tasks using retrieved memory data, combining historical context with current queries to generate informed responses through DSPy-powered reasoning agents.

## Features

- **Memory-Enhanced Reasoning**: Integrates memory context into reasoning processes
- **DSPy Integration**: Utilizes DSPy framework for structured reasoning and prompt optimization
- **Contextual Processing**: Processes tasks with relevant historical information
- **Configurable LLM Support**: Compatible with various language models through environment configuration
- **Flexible Agent Configuration**: YAML-based configuration for reasoning behavior
- **Dynamic Task Processing**: Real-time task processing with memory context

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
LLM_API_KEY=your_api_key_here
LLM_MODEL_NAME=gpt-4o-mini  # Optional, default: gpt-4o-mini
LLM_API_URL=your_custom_api_url  # Optional, for custom endpoints

# Processing Configuration
TASK=default_task_description  # Optional default task
IS_DATAFLOW_END=false         # Dataflow end flag
```

### Agent Configuration (`configs/config.yml`)
Configure the reasoning agent behavior:

```yaml
system:
  env:
    proxy_url: null
    agent_type: reasoner

agent:
  prompt:
    role: Knowledgeable Assistant
    backstory: |
      You are an AI-powered assistant with access to a vast database of knowledge 
      across multiple domains, including history, science, literature, and geography. 
      Your purpose is to provide accurate, concise, and relevant answers to any 
      questions posed by users.
    task: null
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task` | string | Yes | The reasoning task or query to process |
| `memory_context` | string | Yes | Retrieved memory data to inform reasoning |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `reasoner_result` | string | Reasoning result combining task and memory context |

## Usage Example

### Integration with Memory System

This node is typically used as part of a memory-augmented reasoning pipeline:

```yaml
# mem0_dataflow.yml (excerpt)
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

### Standalone Configuration

```yaml
# reasoner-dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      reasoner_result: memory-reasoner/reasoner_result

  - id: memory-reasoner
    build: pip install -e ../../agent-hub/memory-reasoner
    path: memory-reasoner
    outputs:
      - reasoner_result
    inputs:
      task: terminal-input/data
      memory_context: terminal-input/data  # Or from memory system
    env:
      IS_DATAFLOW_END: true
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "LLM_API_KEY=your_api_key" > .env.secret
   echo "LLM_MODEL_NAME=gpt-4o-mini" >> .env.secret
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

4. **The reasoner will:**
   - Receive tasks and memory context
   - Process information using DSPy reasoning
   - Generate context-aware responses
   - Output reasoned results for further processing

## Code Example

The core functionality is implemented in `main.py`:

```python
import json
import os
from mofa.agent_build.base.base_agent import BaseMofaAgent
from mofa.run.run_agent import run_dspy_agent
from mofa.utils.files.read import flatten_dict_simple, read_yaml

class ReasonerAgent(BaseMofaAgent):
    
    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        if config_path is None:
            config_path = self.config_path
        
        self.init_llm_config()
        config = flatten_dict_simple(nested_dict=read_yaml(file_path=config_path))
        
        # Load LLM configuration from environment
        config['model_api_key'] = os.environ.get('LLM_API_KEY')
        config['model_name'] = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')
        
        if os.environ.get('LLM_API_URL', None) is not None:
            config['model_api_url'] = os.environ.get('LLM_API_URL')
        
        return config

    def run(self, memory_context: str, task: str = None, *args, **kwargs):
        config = self.load_config()
        config['task'] = task
        
        # Integrate memory context if available
        if len(memory_context) > 0:
            config['input_fields'] = {"memory_data": memory_context}
            print(config['input_fields'])
        
        # Run DSPy-powered reasoning agent
        agent_result = run_dspy_agent(agent_config=config)
        return agent_result

# Main execution with dynamic node handling
def main():
    parser = argparse.ArgumentParser(description="Reasoner Agent")
    parser.add_argument("--name", type=str, default="arrow-assert")
    parser.add_argument("--task", type=str, default="Paris Olympics")
    parser.add_argument("--memory_context", type=str, default="")
    
    args = parser.parse_args()
    node = Node(args.name)
    
    task = None
    memory_context = None
    load_dotenv('.env.secret')
    
    for event in node:
        if event["type"] == "INPUT" and event['id'] in ['task', 'data']:
            task = event["value"][0].as_py()
            print('task:', task)
        
        if event["type"] == "INPUT" and event['id'] in ["memory_context"]:
            memory_context = load_node_result(event["value"][0].as_py())
            print('memory_context:', memory_context)
        
        if task is not None and memory_context is not None:
            reasoner = ReasonerAgent(
                config_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), ) + '/configs/config.yml',
                llm_config_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), ) + '/.env.secret'
            )
            
            result = reasoner.run(task=task, memory_context=memory_context)
            print('reasoner_result:', result)
            
            output_name = 'reasoner_result'
            node.send_output(
                output_name, 
                pa.array([create_agent_output(
                    agent_name=output_name, 
                    agent_result=result, 
                    dataflow_status=os.getenv('IS_DATAFLOW_END', False)
                )]), 
                event['metadata']
            )
            
            task, memory_context = None, None
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **flask**: For web server capabilities
- **mem0ai** (>= 0.1.97): For memory integration compatibility
- **dspy**: For structured reasoning and prompt optimization (needs to be added to pyproject.toml)
- **python-dotenv**: For environment variable management (needs to be added to pyproject.toml)
- **mofa**: MOFA framework (automatically available in MOFA environment)

**Note**: This node requires `dspy` and `python-dotenv` which should be added to `pyproject.toml`.

## Key Features

### DSPy-Powered Reasoning
- **Structured Prompting**: Uses DSPy framework for optimized prompt engineering
- **Reasoning Optimization**: Automatic optimization of reasoning patterns
- **Modular Components**: Composable reasoning modules for complex tasks
- **Performance Tracking**: Built-in metrics and performance monitoring

### Memory Integration
- **Context Awareness**: Incorporates retrieved memories into reasoning process
- **Contextual Understanding**: Uses historical information to inform current decisions
- **Memory-Guided Responses**: Generates responses based on past interactions and knowledge
- **Dynamic Context**: Adapts reasoning based on available memory data

### Configuration Flexibility
- **Environment-Driven**: Configuration through environment variables
- **Custom Endpoints**: Support for custom LLM API endpoints
- **Model Selection**: Easy switching between different language models
- **Agent Customization**: YAML-based agent personality and behavior configuration

## Reasoning Process

### Input Processing
1. **Task Reception**: Receives reasoning task from input
2. **Memory Context**: Retrieves relevant memory context
3. **Context Integration**: Combines task with memory data
4. **Configuration Loading**: Loads reasoning agent configuration

### DSPy Reasoning Execution
1. **Agent Initialization**: Sets up DSPy reasoning agent with configuration
2. **Context Preparation**: Prepares memory data as input fields
3. **Reasoning Execution**: Runs structured reasoning process
4. **Result Generation**: Produces reasoned output based on task and memory

### Output Delivery
1. **Result Processing**: Formats reasoning results
2. **Output Transmission**: Sends results to downstream components
3. **Status Management**: Handles dataflow status and completion signals

## Use Cases

### Knowledge-Augmented QA Systems
- **Historical Context**: Answer questions using past conversation history
- **Domain Expertise**: Provide domain-specific answers using accumulated knowledge
- **Personalized Responses**: Generate responses tailored to user history and preferences
- **Learning Systems**: Improve responses over time through memory integration

### Decision Support Systems
- **Historical Analysis**: Make decisions based on past outcomes and experiences
- **Pattern Recognition**: Identify patterns from memory to inform current decisions
- **Risk Assessment**: Evaluate risks using historical data and context
- **Strategic Planning**: Develop strategies based on past successes and failures

### Educational Applications
- **Adaptive Learning**: Adjust teaching methods based on student history
- **Progress Tracking**: Monitor learning progress and adapt content accordingly
- **Personalized Tutoring**: Provide personalized educational experiences
- **Knowledge Assessment**: Evaluate understanding based on interaction history

## Advanced Configuration

### Custom Reasoning Agents
```yaml
agent:
  prompt:
    role: Domain Expert
    backstory: |
      You are a specialized expert in [specific domain] with years of experience
      analyzing complex problems and providing strategic insights based on
      historical data and current context.
    task: |
      Analyze the given task using both current information and historical context
      to provide comprehensive, actionable insights.
```

### Multi-Model Configuration
```bash
# Support for different models based on task complexity
LLM_MODEL_NAME=gpt-4o          # For complex reasoning
LLM_FALLBACK_MODEL=gpt-4o-mini # For simple tasks
LLM_API_URL=custom_endpoint    # Custom API endpoint
```

### Memory Context Optimization
```python
def optimize_memory_context(memory_data, task):
    # Filter and rank memory based on task relevance
    relevant_memories = filter_memories(memory_data, task)
    ranked_memories = rank_by_relevance(relevant_memories, task)
    return format_for_reasoning(ranked_memories)
```

## Integration Patterns

### Memory-Reasoner-Action Loop
```
Memory Search ’ Context Retrieval ’ Reasoning ’ Action ’ Memory Update
      “              “              “         “         “
   Query         Historical      Informed   Action    Updated
  Processing     Context       Decision   Execution   Knowledge
```

### Multi-Agent Collaboration
```yaml
# Collaborative reasoning with specialized agents
Scientific Reasoner ’ Memory Context ’ Business Reasoner ’ Decision Synthesis
```

## Performance Optimization

### Reasoning Efficiency
- **Context Filtering**: Filter memory context to most relevant information
- **Prompt Optimization**: Use DSPy optimization for improved reasoning performance
- **Model Selection**: Choose appropriate models based on task complexity
- **Caching**: Cache reasoning results for similar tasks and contexts

### Memory Integration Optimization
- **Context Summarization**: Summarize large memory contexts for efficiency
- **Relevance Scoring**: Score and rank memory items by relevance
- **Context Limits**: Set limits on memory context size for optimal performance
- **Parallel Processing**: Process memory and reasoning tasks in parallel

## Troubleshooting

### Common Issues
1. **DSPy Import Errors**: Ensure DSPy is properly installed and configured
2. **Memory Context Format**: Verify memory context is properly formatted
3. **Configuration Loading**: Check YAML configuration file syntax
4. **API Connectivity**: Verify LLM API connectivity and credentials

### Debug Tips
- Monitor task and memory context inputs
- Enable detailed logging for DSPy reasoning processes
- Test with simplified tasks and memory contexts first
- Verify configuration loading and environment variable setup
- Check LLM API response times and quotas

## Security Considerations

### Memory Privacy
- **Context Sanitization**: Sanitize sensitive information in memory contexts
- **Access Control**: Implement proper access controls for memory data
- **Data Encryption**: Consider encrypting sensitive memory contexts
- **Audit Logging**: Log reasoning operations for security auditing

## Contributing

1. Test with various reasoning scenarios and memory contexts
2. Optimize DSPy integration for better reasoning performance
3. Add support for additional reasoning frameworks
4. Enhance memory context processing and optimization

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://mofa.ai/)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [DSPy Framework](https://github.com/stanfordnlp/dspy)
- [Mem0 AI](https://github.com/mem0ai/mem0)