# Deep Search Node

A sophisticated MOFA node that performs comprehensive deep research using AI-powered multi-stage analysis. This node combines web search capabilities with advanced LLM reasoning to provide thorough, well-structured research reports on any given topic.

## Features

- **Multi-Stage Research Process**: Implements 5 distinct thinking stages (context extraction, intent analysis, source evaluation, contradiction checking, synthesis)
- **Serper Integration**: Uses Serper API for comprehensive web search results
- **LLM-Powered Analysis**: Leverages OpenAI models for intelligent content generation and analysis
- **Streaming Output**: Provides real-time streaming responses for better user experience
- **Article Processing**: Advanced article deduplication, filtering, and relevance ranking
- **Source Credibility Evaluation**: Assesses and ranks sources based on trustworthiness
- **Comprehensive Synthesis**: Generates detailed final reports integrating all research stages

## Installation

Install the package in development mode:

```bash
pip install -e .
```

**Note**: This node requires additional dependencies that should be added to `pyproject.toml`:
- `numpy` - for numerical computations
- `playwright` - for web interactions (imported but not in dependencies)

## Configuration

### Environment Configuration (`.env.secret`)
Required environment variables:

```bash
# OpenAI API Configuration
LLM_API_KEY=your_openai_api_key_here
LLM_BASE_URL=https://api.openai.com/v1  # optional, for custom endpoints
LLM_MODEL_NAME=gpt-4o  # optional, defaults to gpt-4o

# Serper API Configuration
SERPER_API_KEY=your_serper_api_key_here
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_query` | string | Yes | The research topic or question to investigate |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `deep_search_result` | string (JSON) | Streaming research results with thinking stages and final synthesis |

## Usage Example

### Basic Dataflow Configuration

```yaml
# deepsearch-dataflow.yml
nodes:
  - id: dora-openai-server
    build: pip install -e ../../node-hub/openai-server-stream
    path: openai-server-stream
    outputs:
      - v3/chat/completions
    inputs:      
      v3/chat/completions:
        source: deep-search-agent/deep_search_result
        queue_size: 1000

  - id: deep-search-agent
    build: pip install -e ../../agent-hub/deep-search
    path: deep-search
    outputs:
      - deep_search_result
    inputs:
      user_query: dora-openai-server/v3/chat/completions
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "LLM_API_KEY=your_openai_key" > .env.secret
   echo "SERPER_API_KEY=your_serper_key" >> .env.secret
   echo "LLM_MODEL_NAME=gpt-4o" >> .env.secret
   ```

2. **Start the MOFA framework:**
   ```bash
   dora up
   ```

3. **Build and start the dataflow:**
   ```bash
   dora build deepsearch-dataflow.yml
   dora start deepsearch-dataflow.yml
   ```

4. **Send research queries:**
   Examples:
   - "Latest developments in artificial intelligence"
   - "Climate change impact on renewable energy"
   - "Blockchain technology in healthcare applications"

## Code Example

The core functionality is implemented in `main.py`:

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from mofa.kernel.tools.web_search import search_web_with_serper
import json
import time

@run_agent
def run(agent: MofaAgent):
    user_query = agent.receive_parameter('user_query')
    
    # Search for articles using Serper
    raw_articles = search_web_with_serper(
        query=user_query, 
        subscription_key=os.getenv("SERPER_API_KEY")
    )
    
    # Process and filter articles
    processor = ArticleProcessor(raw_articles)
    processed_articles = processor.process()
    selected_articles = processed_articles[:20]
    
    # Initialize LLM client and research generator
    llm_client = LLMClient(model_name=os.getenv("LLM_MODEL_NAME", "gpt-4o"))
    generator = ResearchGenerator(articles=selected_articles, llm_client=llm_client)
    
    # Generate streaming research results
    for chunk in generator.generate_stream(user_query=user_query):
        agent.send_output(
            agent_output_name='deep_search_result',
            agent_result=json.dumps(chunk, indent=2)
        )
        time.sleep(0.005)  # Small delay for streaming

def main():
    agent = MofaAgent(agent_name='DeepInquire')
    run(agent=agent)
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **python-dotenv**: For environment variable management
- **openai**: For OpenAI API integration
- **numpy**: For numerical computations (needs to be added to pyproject.toml)
- **playwright**: For web interactions (needs to be added to pyproject.toml)
- **mofa**: MOFA framework (automatically available in MOFA environment)

## Research Process Stages

### 1. Context Extraction (📝)
- Isolates the most informative snippets from articles
- Focuses on top 3 most relevant articles
- Extracts key contextual information

### 2. Intent Analysis (🔍)
- Analyzes core user intent from extracted context
- Determines research objectives and scope
- Identifies specific areas of focus

### 3. Source Evaluation (📊)
- Ranks articles based on source trustworthiness
- Prioritizes credible sources (journals, reports, authoritative websites)
- Assesses information reliability

### 4. Contradiction Check (⚠️)
- Cross-references articles for information consistency
- Identifies conflicting information across sources
- Validates factual accuracy

### 5. Synthesis (🧠)
- Integrates validated information from all stages
- Creates comprehensive understanding
- Generates structured insights

## Output Format

The node generates streaming JSON outputs with the following structure:

```json
{
  "type": "thinking|content|completion",
  "content": "Generated content chunk",
  "articles": [{"title": "...", "url": "...", "snippet": "..."}],
  "metadata": {"stage": "stage_name"},
  "id": "stage_id-substep_id"
}
```

## Use Cases

### Academic Research
- **Literature Review**: Comprehensive analysis of academic topics
- **Trend Analysis**: Identifying emerging patterns in research fields
- **Gap Identification**: Finding research opportunities and unexplored areas

### Business Intelligence
- **Market Research**: In-depth analysis of market trends and opportunities
- **Competitive Analysis**: Understanding competitor strategies and positioning
- **Technology Assessment**: Evaluating emerging technologies and their potential

### Journalism and Content Creation
- **Investigative Research**: Thorough investigation of complex topics
- **Fact-Checking**: Verification of claims across multiple sources
- **Background Research**: Comprehensive context for news stories

## Advanced Features

### Article Processing Pipeline
- **Deduplication**: Removes duplicate articles by URL
- **Quality Filtering**: Ranks articles by snippet length and relevance
- **Source Prioritization**: Prefers authoritative sources

### Streaming Architecture
- **Real-time Output**: Provides immediate feedback during processing
- **Chunked Processing**: Handles large datasets efficiently
- **Progress Tracking**: Clear indication of research progress

## Troubleshooting

### Common Issues
1. **API Key Errors**: Ensure both OpenAI and Serper API keys are valid
2. **Rate Limiting**: Be aware of API rate limits for both services
3. **Network Issues**: Verify stable internet connection for web searches
4. **Memory Usage**: Large research topics may consume significant memory

### Debug Tips
- Enable detailed logging with environment variables
- Check API key validity and quotas
- Monitor network connectivity during searches
- Adjust MAX_ARTICLES constant for memory optimization

## Contributing

1. Test with various research topics and domains
2. Optimize article selection algorithms
3. Add support for additional search providers
4. Implement caching mechanisms for improved performance

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Serper API](https://serper.dev/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)