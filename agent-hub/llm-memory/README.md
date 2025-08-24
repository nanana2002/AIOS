# Deepseek Node

A MOFA node that provides AI-powered text analysis and content generation using the Deepseek API. This node specializes in synthesizing information from multiple sources, particularly web search results, to deliver accurate, insightful responses in Markdown format.

## Features

- **Deepseek AI Integration**: Utilizes the powerful deepseek-chat model for advanced language processing
- **Multi-Source Analysis**: Processes user queries alongside web search data for comprehensive responses
- **Markdown Output**: Generates well-formatted responses with proper structure and source URLs
- **Configurable Prompts**: Uses YAML-based configuration for flexible prompt management
- **Real-time Processing**: Provides immediate responses without streaming delays

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

### Environment Configuration (`.env.secret`)
Required environment variables:

```bash
# Deepseek API Configuration
LLM_API_KEY=your_deepseek_api_key_here
```

### Agent Configuration (`configs/agent.yml`)
The node uses a YAML configuration file to define the AI agent's behavior:

```yaml
agent:
  prompt:
    role: You are an advanced AI agent specializing in analyzing and synthesizing information provided by users.
    backstory: |
      Developed to assist users in making sense of pre-collected data, your main function is to integrate and analyze the information provided to you.
    answer: Optimize the output to be in Markdown format. Include the URLs of the sources in the output.
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The user question or topic to analyze |
| `serper_result` | JSON | Yes | Web search results from Serper API for context |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `deepseek_result` | string | AI-generated analysis and synthesis in Markdown format with source URLs |

## Usage Example

### Basic Dataflow Configuration

```yaml
# deepseek_serper_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      serper_result: serper-agent/serper_result
      deepseek_result: deepseek-agent/deepseek_result

  - id: serper-agent
    build: pip install -e ../../agent-hub/serper-search
    path: serper-search
    outputs:
      - serper_result
    inputs:
      query: terminal-input/data
    env:
      IS_DATAFLOW_END: false

  - id: deepseek-agent
    build: pip install -e ../../agent-hub/deepseek
    path: deepseek
    outputs:
      - deepseek_result
    inputs:
      query: terminal-input/data
      serper_result: serper-agent/serper_result
    env:
      IS_DATAFLOW_END: true
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "LLM_API_KEY=your_deepseek_api_key" > .env.secret
   ```

2. **Start the MOFA framework:**
   ```bash
   dora up
   ```

3. **Build and start the dataflow:**
   ```bash
   dora build deepseek_serper_dataflow.yml
   dora start deepseek_serper_dataflow.yml
   ```

4. **Send queries through terminal input:**
   Examples:
   - "Analyze the latest developments in renewable energy"
   - "What are the current trends in artificial intelligence?"
   - "Summarize the impact of climate change on agriculture"

## Code Example

The core functionality is implemented in `main.py`:

```python
from mofa.agent_build.base.base_agent import MofaAgent
import os
from dotenv import load_dotenv
from openai import OpenAI
from deepseek import agent_config_dir_path
from mofa.utils.files.read import read_yaml

def main():
    agent = MofaAgent(agent_name='deepseek')
    while True:
        # Load environment configuration
        load_dotenv(agent_config_dir_path + '/.env.secret')
        
        # Initialize Deepseek client
        client = OpenAI(
            api_key=os.getenv('LLM_API_KEY'), 
            base_url="https://api.deepseek.com"
        )
        
        # Load agent configuration
        config = read_yaml(file_path=agent_config_dir_path + '/configs/agent.yml')
        system_prompt = json.dumps(config.get('agent').get('prompt'))
        
        # Get inputs
        user_query = agent.receive_parameter(parameter_name='query')
        serper_data = agent.receive_parameter(parameter_name='serper_result')
        
        # Generate response
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"user query: {user_query} serper search data: {json.dumps(serper_data)}"}
            ],
            stream=False
        )
        
        # Send output
        agent.send_output(
            agent_output_name='deepseek_result', 
            agent_result=response.choices[0].message.content
        )
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **openai**: For Deepseek API integration (compatible OpenAI client)
- **python-dotenv**: For environment variable management (needs to be added to pyproject.toml)
- **mofa**: MOFA framework (automatically available in MOFA environment)

**Note**: This node requires `python-dotenv` which should be added to `pyproject.toml`.

## Key Features

### Advanced Language Processing
- Utilizes Deepseek's cutting-edge language model for sophisticated text analysis
- Capable of understanding context from multiple information sources
- Generates coherent, well-structured responses

### Information Synthesis
- Combines user queries with web search results for comprehensive analysis
- Identifies key insights from disparate data sources
- Provides contextually relevant answers with proper attribution

### Markdown Formatting
- Automatically formats responses in clean Markdown
- Includes source URLs for transparency and verification
- Structures content for optimal readability

## Use Cases

### Research and Analysis
- **Academic Research**: Synthesizing information from multiple scholarly sources
- **Market Analysis**: Analyzing trends and data from various market reports
- **Technical Documentation**: Creating comprehensive technical summaries

### Content Creation
- **Article Writing**: Generating well-researched articles with proper citations
- **Report Generation**: Creating structured reports from raw data
- **Summary Creation**: Condensing complex information into digestible formats

### Decision Support
- **Business Intelligence**: Analyzing market data for strategic decisions
- **Policy Analysis**: Synthesizing information for policy recommendations
- **Competitive Analysis**: Understanding market landscape from multiple sources

## Integration Patterns

### With Search Agents
- Commonly paired with `serper-search` agent for web data collection
- Processes search results to extract actionable insights
- Maintains source attribution throughout analysis

### Terminal Input Integration
- Works seamlessly with terminal input for interactive queries
- Supports real-time question-answering workflows
- Enables dynamic query processing

## Troubleshooting

### Common Issues
1. **API Key Errors**: Verify Deepseek API key is valid and has sufficient credits
2. **Configuration Issues**: Ensure `agent.yml` file is properly formatted
3. **Missing Dependencies**: Install all required packages including `python-dotenv`
4. **Path Issues**: Verify `agent_config_dir_path` points to correct configuration directory

### Debug Tips
- Check API key validity and quota limits
- Verify configuration file paths and formats
- Monitor network connectivity for API calls
- Review input data structure for proper JSON formatting

## Performance Considerations

### Response Time
- Non-streaming responses provide complete analysis in single output
- Processing time depends on query complexity and search result volume
- Optimized for quality over speed

### Resource Usage
- Minimal local resource consumption (computation handled by Deepseek API)
- Memory usage scales with input data size
- Network bandwidth required for API communications

## Contributing

1. Test with various query types and search result formats
2. Optimize prompt engineering for better response quality
3. Add support for additional output formats
4. Implement response caching for improved performance

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Deepseek API](https://api.deepseek.com/)
- [OpenAI Python Client](https://github.com/openai/openai-python)
