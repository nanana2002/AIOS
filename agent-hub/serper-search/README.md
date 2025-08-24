# Serper Search Node

A MOFA node that provides web search functionality through the Serper API. This node enables comprehensive web search capabilities with high-quality search results from Google's search index via the Serper service.

## Features

- **Serper API Integration**: High-quality web search results through Serper's Google Search API
- **Configurable Search Results**: Customizable number of search results
- **Environment Configuration**: Secure API key management through environment variables
- **JSON Output**: Returns structured search results for easy processing
- **Error Handling**: Robust error handling for API failures and network issues
- **MOFA Integration**: Seamless integration with MOFA agent framework

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

### Environment Configuration (`.env.secret`)
Required environment variables:

```bash
# Serper API Configuration
SERPER_API_KEY=your_serper_api_key_here

# Optional: Number of search results (default: 10)
SEAPER_SEARCH_NUM=10
```

**Note**: You need to obtain a Serper API key from [serper.dev](https://serper.dev/). Serper provides free tier access with limited searches per month.

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The search query to execute |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `serper_result` | string (JSON) | Search results containing titles, URLs, snippets, and metadata |

## Usage Example

### Basic Dataflow Configuration

```yaml
# serper-search-dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      serper_result: serper-search-agent/serper_result
  - id: serper-search-agent
    build: pip install -e ../../agent-hub/serper-search
    path: serper-search
    outputs:
      - serper_result
    inputs:
      query: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "SERPER_API_KEY=your_serper_api_key" > .env.secret
   echo "SEAPER_SEARCH_NUM=10" >> .env.secret
   ```

2. **Start the MOFA framework:**
   ```bash
   dora up
   ```

3. **Build and start the dataflow:**
   ```bash
   dora build serper-search-dataflow.yml
   dora start serper-search-dataflow.yml
   ```

4. **Perform searches:**
   Enter search queries and receive comprehensive search results from Google.

## Code Example

The core functionality is implemented in `main.py`:

```python
import os
from dotenv import load_dotenv
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from mofa.kernel.tools.web_search import search_web_with_serper
from serper_search import agent_config_dir_path

@run_agent
def run(agent: MofaAgent):
    # Load environment variables
    load_dotenv(os.path.join(agent_config_dir_path, '.env.secret'))
    load_dotenv('.env.secret')

    # Receive the user query
    user_query = agent.receive_parameter('query')

    # Perform web search using Serper
    serper_result = search_web_with_serper(
        query=user_query, 
        subscription_key=os.getenv("SERPER_API_KEY"),
        search_num=os.getenv('SEAPER_SEARCH_NUM', 10)
    )

    # Send the search results back to the agent
    agent.send_output(agent_output_name='serper_result', agent_result=serper_result)

def main():
    agent = MofaAgent(agent_name='serper_search')
    run(agent=agent)
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **python-dotenv**: For environment variable management
- **mofa**: MOFA framework (automatically available in MOFA environment)

## Key Features

### Search Capabilities
- **Google Search Index**: Access to Google's comprehensive search index through Serper
- **High-Quality Results**: Professional-grade search results with rich metadata
- **Real-time Results**: Current and up-to-date search information
- **Multiple Result Types**: Web pages, news, images, and other content types

### Configuration Options
- **Result Count**: Configurable number of search results (default: 10)
- **API Key Management**: Secure environment variable-based configuration
- **Multiple Config Paths**: Support for both local and agent-specific configurations
- **Flexible Parameters**: Easy customization of search parameters

### Integration Features
- **MOFA Framework**: Full integration with MOFA's dataflow system
- **JSON Output**: Structured data format for easy processing
- **Error Resilience**: Robust handling of API errors and network issues
- **Environment Flexibility**: Development and production environment support

## Use Cases

### Research and Information Gathering
- **Academic Research**: Gather information from web sources for research projects
- **Market Research**: Collect market intelligence and competitive information
- **News Monitoring**: Stay updated with latest news and trends
- **Fact Checking**: Verify information across multiple web sources

### Content Creation and Analysis
- **Content Research**: Research topics for content creation
- **SEO Analysis**: Analyze search results for SEO insights
- **Trend Analysis**: Identify trending topics and keywords
- **Competitive Analysis**: Monitor competitor online presence

### AI and Automation
- **AI-Powered Search**: Integrate web search into AI workflows
- **Automated Research**: Automate information gathering processes
- **Data Enrichment**: Enrich datasets with web-sourced information
- **Knowledge Base Updates**: Keep knowledge bases current with web data

## Search Result Format

The node returns JSON data with comprehensive search information:

```json
{
  "searchParameters": {
    "q": "your search query",
    "type": "search",
    "engine": "google"
  },
  "organic": [
    {
      "title": "Page Title",
      "link": "https://example.com/page",
      "snippet": "Page description and relevant content snippet",
      "position": 1
    }
  ],
  "knowledgeGraph": {
    "title": "Knowledge Graph Title",
    "type": "Entity Type",
    "description": "Entity description"
  },
  "relatedSearches": [
    {
      "query": "Related search query"
    }
  ]
}
```

## Advanced Configuration

### Custom Search Parameters
```python
# Custom search with additional parameters
serper_result = search_web_with_serper(
    query=user_query,
    subscription_key=os.getenv("SERPER_API_KEY"),
    search_num=20,  # More results
    country="us",   # Geographic location
    language="en"   # Language preference
)
```

### Multiple API Keys
```bash
# Rotate between multiple API keys for higher rate limits
SERPER_API_KEY_1=your_first_api_key
SERPER_API_KEY_2=your_second_api_key
SERPER_API_KEY_3=your_third_api_key
```

### Result Filtering
```python
def filter_search_results(results, keywords):
    """Filter search results based on keywords"""
    filtered_results = []
    for result in results.get('organic', []):
        if any(keyword.lower() in result['snippet'].lower() for keyword in keywords):
            filtered_results.append(result)
    return filtered_results
```

## Troubleshooting

### Common Issues
1. **API Key Errors**: 
   - Verify your Serper API key is valid and active
   - Check if you have remaining API quota
   - Ensure the API key is correctly set in environment variables

2. **Rate Limiting**:
   - Monitor your API usage against Serper's rate limits
   - Implement delays between requests if needed
   - Consider upgrading your Serper plan for higher limits

3. **Network Issues**:
   - Check internet connectivity
   - Verify Serper service status
   - Implement retry logic for transient failures

### Debug Tips
- Test your API key directly with Serper's API documentation
- Monitor API usage in your Serper dashboard
- Use smaller search result counts for testing
- Enable detailed logging to trace API requests

### API Limits and Pricing
```bash
# Serper API Tiers (as of 2024)
# Free Tier: 2,500 searches per month
# Hobby: $50/month for 50,000 searches
# Pro: $200/month for 200,000 searches
# Enterprise: Custom pricing
```

## Performance Considerations

### Optimization
- **Query Optimization**: Craft efficient search queries to get better results
- **Result Caching**: Cache search results for repeated queries
- **Rate Management**: Respect API rate limits and implement backoff strategies
- **Error Handling**: Implement proper retry logic with exponential backoff

### Scalability
- **Multiple API Keys**: Use multiple API keys for higher throughput
- **Load Balancing**: Distribute requests across multiple keys
- **Usage Monitoring**: Track API usage and costs
- **Result Processing**: Efficiently process large result sets

## Configuration File Support

The node supports agent-specific configuration files:

```yaml
# serper_search/configs/agent.yml
api_settings:
  default_search_count: 10
  timeout: 30
  retry_attempts: 3

search_filters:
  safe_search: moderate
  country: "us"
  language: "en"
```

## Contributing

1. Add support for additional Serper API features (images, news, etc.)
2. Implement result caching and optimization
3. Add search result filtering and ranking capabilities
4. Improve error handling and retry mechanisms

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Serper API](https://serper.dev/)
- [Serper API Documentation](https://serper.dev/api-documentation)