# Browser Use Connector Node

A MOFA node that integrates AI-powered browser automation using the browser-use library and ChatOpenAI. This node enables intelligent web interactions by combining large language models with automated browser controls to perform complex web tasks.

## Features

- **AI-Powered Browser Automation**: Uses browser-use library for intelligent web interactions
- **LLM Integration**: Leverages ChatOpenAI for natural language understanding and task planning
- **Asynchronous Processing**: Built with asyncio for efficient non-blocking browser operations
- **Environment Configuration**: Configurable LLM settings through environment variables
- **MOFA Framework Integration**: Standard MOFA agent pattern for seamless workflow integration
- **Flexible Model Support**: Supports various OpenAI models with custom API endpoints

## Installation

Install the package in development mode:

```bash
pip install -e .
```

**Note**: This node requires additional dependencies that should be added to `pyproject.toml`:
- `langchain-openai` - for OpenAI LLM integration
- `python-dotenv` - for environment variable management

## Configuration

### Environment Configuration (`.env.secret`)
Required environment variables for LLM access:

```bash
# OpenAI API Configuration
LLM_API_KEY=your_openai_api_key_here
LLM_BASE_URL=https://api.openai.com/v1  # or custom endpoint
LLM_MODEL_NAME=gpt-4o  # optional, defaults to gpt-4o
```

### Agent Configuration (`configs/agent.yml`)
Basic agent configuration file (currently minimal).

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | string | Yes | Natural language description of the browser task to perform |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_result` | string | Final result from the browser automation task |

## Usage Example

### Basic Dataflow Configuration

```yaml
# hello_browser_use_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      agent_response: browser_use_connector-agent/agent_result
  - id: browser_use_connector-agent
    build: pip install -e ../../agent-hub/browser-use-connector
    path: browser-use-connector
    outputs:
      - agent_result
    inputs:
      question: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "LLM_API_KEY=your_api_key" > .env.secret
   echo "LLM_BASE_URL=https://api.openai.com/v1" >> .env.secret
   echo "LLM_MODEL_NAME=gpt-4o" >> .env.secret
   ```

2. **Start the MOFA framework:**
   ```bash
   dora up
   ```

3. **Build and start the dataflow:**
   ```bash
   dora build hello_browser_use_dataflow.yml
   dora start hello_browser_use_dataflow.yml
   ```

4. **Send browser task:**
   Input natural language descriptions like:
   - "Navigate to Google and search for Python tutorials"
   - "Go to GitHub and find the most starred Python repositories"
   - "Visit a news website and summarize the top headlines"

## Code Example

The core functionality is implemented in `main.py`:

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='.env.secret', override=True)
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
DEFAULT_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o")

@run_agent
def run(agent: MofaAgent):
    # Receive user question
    question = agent.receive_parameter('question')
    
    # Run browser automation asynchronously
    history = asyncio.run(run_browser_use(question))
    
    # Send result
    agent.send_output(
        agent_output_name='agent_result',
        agent_result=history.final_result()
    )

async def run_browser_use(question: str):
    # Create browser automation agent
    agent = Agent(
        task=question,
        llm=ChatOpenAI(
            model=DEFAULT_MODEL_NAME,
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL
        ),
    )
    # Execute the task
    return await agent.run()

def main():
    agent = MofaAgent(agent_name='browser-use-connector')
    run(agent=agent)
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **browser-use** (0.1.40): Core browser automation library
- **langchain-openai**: For OpenAI LLM integration (needs to be added to pyproject.toml)
- **python-dotenv**: For environment variable management (needs to be added to pyproject.toml)
- **mofa**: MOFA framework (automatically available in MOFA environment)

## Browser Automation Capabilities

The browser-use library provides:

### Web Navigation
- Navigate to websites and web applications
- Handle page loading and dynamic content
- Manage browser tabs and windows

### Element Interaction
- Click buttons, links, and interactive elements
- Fill forms and input fields
- Handle dropdowns and selections

### Data Extraction
- Extract text content from web pages
- Capture screenshots and visual content
- Parse structured data from tables and lists

### Advanced Features
- Handle JavaScript-heavy applications
- Manage cookies and session state
- Perform multi-step workflows

## Example Use Cases

### Web Research
```python
# Task: "Search for recent developments in AI and summarize top 3 results"
# The agent will:
# 1. Navigate to a search engine
# 2. Enter the search query
# 3. Extract relevant information
# 4. Summarize findings
```

### E-commerce Automation
```python
# Task: "Find the cheapest laptop under $1000 on an e-commerce site"
# The agent will:
# 1. Navigate to the website
# 2. Use search and filters
# 3. Compare prices
# 4. Return recommendations
```

### Content Monitoring
```python
# Task: "Check news websites for updates on specific topics"
# The agent will:
# 1. Visit multiple news sources
# 2. Look for relevant articles
# 3. Extract key information
# 4. Compile a summary report
```

## Troubleshooting

### Common Issues
1. **Missing API Key**: Ensure `LLM_API_KEY` is set in `.env.secret`
2. **Browser Dependencies**: browser-use may require additional browser binaries
3. **Async Execution**: Ensure proper async/await usage in custom implementations
4. **Rate Limiting**: Be aware of API rate limits for the configured LLM

### Debug Tips
- Enable `WRITE_LOG: true` in dataflow configuration
- Check browser-use documentation for browser setup requirements
- Verify network connectivity for API calls

## Contributing

1. Ensure your code follows the existing async patterns
2. Add missing dependencies to pyproject.toml
3. Test with various browser automation scenarios
4. Update documentation for new capabilities

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Browser-use Library](https://github.com/browser-use/browser-use)
- [LangChain OpenAI](https://python.langchain.com/docs/integrations/llms/openai)