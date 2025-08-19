# Firecrawl Agent Node

A MOFA node that provides advanced web crawling and deep research capabilities using the Firecrawl API. This node specializes in comprehensive web analysis, extracting structured information from websites with AI-powered analysis and insights.

## Features

- **Advanced Web Crawling**: Utilizes Firecrawl API for comprehensive website analysis
- **Deep Research Mode**: Performs multi-depth crawling with intelligent content extraction
- **AI-Powered Analysis**: Includes built-in analysis prompts for structured data extraction
- **Configurable Parameters**: Customizable crawl depth, URL limits, and time constraints
- **Activity Monitoring**: Real-time feedback on crawling progress and activities
- **Structured Output**: Returns both source data and final analysis in JSON format

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

### Environment Configuration (`.env.secret`)
Required environment variables:

```bash
# Firecrawl API Configuration
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Optional Configuration
FIRECRAWL_MAXDEPTH=3           # Maximum crawl depth (default: 3)
FIRECRAWL_MAXURLS=15          # Maximum URLs to analyze (default: 15)
ANALYSIS_PROMPT=custom_prompt  # Custom analysis prompt (optional)
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The search query or topic for deep research |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `firecrawl_agent_result` | string (JSON) | Combined source data and analysis results from web crawling |

## Usage Example

### Basic Dataflow Configuration

```yaml
# firecrawl_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      firecrawl_agent_result: firecrawl-agent/firecrawl_agent_result

  - id: firecrawl-agent
    build: pip install -e ../../agent-hub/firecrawl-agent
    path: firecrawl-agent
    outputs:
      - firecrawl_agent_result
    inputs:
      query: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "FIRECRAWL_API_KEY=your_firecrawl_api_key" > .env.secret
   echo "FIRECRAWL_MAXDEPTH=3" >> .env.secret
   echo "FIRECRAWL_MAXURLS=15" >> .env.secret
   ```

2. **Start the MOFA framework:**
   ```bash
   dora up
   ```

3. **Build and start the dataflow:**
   ```bash
   dora build firecrawl_dataflow.yml
   dora start firecrawl_dataflow.yml
   ```

4. **Send research queries:**
   Examples:
   - "Research information about Elon Musk"
   - "Analyze the latest developments in quantum computing"
   - "Find detailed information about OpenAI leadership"

## Code Example

The core functionality is implemented in `main.py`:

```python
from firecrawl.firecrawl import FirecrawlApp
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
import json
import os
from dotenv import load_dotenv

class FireCrawl:
    def __init__(self, api_key: str = None, env_file: str = '.env.secret', crawl_params: dict = None):
        if api_key is None:
            load_dotenv(env_file)
            api_key = os.getenv("FIRECRAWL_API_KEY")
        
        self.crawl = FirecrawlApp(api_key=api_key)
        
        if crawl_params is None:
            crawl_params = {
                "maxDepth": os.getenv('FIRECRAWL_MAXDEPTH', 3),
                "timeLimit": 180,  # Time limit in seconds
                "maxUrls": os.getenv('FIRECRAWL_MAXURLS', 15)
            }
        self.crawl_params = crawl_params

    def deep_research(self, query: str, analysis_prompt: str = None):
        if analysis_prompt is None:
            analysis_prompt = """
            Development History: The speaker's growth path in the industry, major accomplishments, and technological breakthroughs.
            Personal Story: The speaker's background, career transitions, and challenges faced along the way.
            Educational Background: The speaker's education history, including degrees and universities.
            Patents: Whether the speaker holds any technological patents.
            Professional Experience: The speaker's work history, including companies and key projects.
            """
        
        results = self.crawl.deep_research(
            query=query,
            max_depth=os.getenv('FIRECRAWL_MAXDEPTH', 3),
            max_urls=os.getenv('FIRECRAWL_MAXURLS', 10),
            on_activity=self.on_activity,
            analysis_prompt=analysis_prompt
        )
        
        source_data = results['data']['sources']
        analysis_data = results['data']['finalAnalysis']
        return source_data, analysis_data

@run_agent
def run(agent: MofaAgent):
    load_dotenv('.env.secret')
    query = agent.receive_parameter('query')
    
    app = FireCrawl()
    scrape_result = json.dumps(app.deep_research(query=query))
    
    agent.send_output(
        agent_output_name='firecrawl_agent_result',
        agent_result=scrape_result
    )
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **firecrawl** (>= 2.4.3): For web crawling and content extraction
- **python-dotenv**: For environment variable management (needs to be added to pyproject.toml)
- **mofa**: MOFA framework (automatically available in MOFA environment)

**Note**: This node requires `python-dotenv` which should be added to `pyproject.toml`.

## Key Features

### Deep Research Capabilities
- **Multi-Depth Crawling**: Recursively crawls websites up to specified depth
- **Intelligent Content Extraction**: Uses AI to identify and extract relevant content
- **Source Tracking**: Maintains detailed records of all crawled sources
- **Activity Monitoring**: Provides real-time feedback on crawling progress

### Configurable Analysis
- **Custom Prompts**: Supports custom analysis prompts for specific research needs
- **Default Templates**: Includes comprehensive default analysis templates
- **Structured Output**: Returns both raw source data and analyzed insights
- **Flexible Parameters**: Adjustable crawl depth, URL limits, and time constraints

### Professional Research Focus
- **Background Analysis**: Extracts professional background and career history
- **Educational Information**: Identifies educational background and qualifications
- **Patent Research**: Discovers patent information and intellectual property
- **Social Media Integration**: Analyzes social media presence and contributions

## Use Cases

### Professional Research
- **Executive Profiling**: Comprehensive research on business leaders and executives
- **Academic Research**: Detailed analysis of researchers and their contributions
- **Competitive Intelligence**: In-depth analysis of competitors and their leadership
- **Due Diligence**: Background research for business partnerships and investments

### Content Creation
- **Biography Writing**: Gathering comprehensive information for biographical content
- **Interview Preparation**: Research for podcast or interview preparation
- **Article Research**: Background information for news articles and features
- **Speaker Profiles**: Detailed profiles for conference speakers and presenters

### Business Intelligence
- **Market Research**: Analysis of key players in specific industries
- **Talent Acquisition**: Research for executive recruiting and hiring decisions
- **Partnership Assessment**: Background research on potential business partners
- **Investment Analysis**: Due diligence research for investment decisions

## Advanced Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FIRECRAWL_MAXDEPTH` | 3 | Maximum crawl depth for web analysis |
| `FIRECRAWL_MAXURLS` | 15 | Maximum number of URLs to crawl |
| `ANALYSIS_PROMPT` | Default template | Custom analysis prompt for structured extraction |

### Custom Analysis Prompts

You can customize the analysis focus by setting the `ANALYSIS_PROMPT` environment variable:

```bash
export ANALYSIS_PROMPT="Focus on: Technical expertise, Leadership experience, Innovation track record, Industry recognition"
```

### Crawl Parameters

The node supports various crawl parameters:

```python
crawl_params = {
    "maxDepth": 3,        # How deep to crawl
    "timeLimit": 180,     # Maximum time in seconds
    "maxUrls": 15        # Maximum URLs to analyze
}
```

## Output Format

The node returns a JSON string containing two main components:

```json
[
  {
    "sources": [
      {
        "url": "https://example.com",
        "title": "Page Title",
        "content": "Extracted content...",
        "metadata": {...}
      }
    ],
    "finalAnalysis": {
      "summary": "Comprehensive analysis...",
      "key_findings": [...],
      "structured_data": {...}
    }
  }
]
```

## Troubleshooting

### Common Issues
1. **API Key Errors**: Ensure Firecrawl API key is valid and has sufficient credits
2. **Rate Limiting**: Be aware of API rate limits and adjust crawl parameters accordingly
3. **Timeout Issues**: Increase time limit for complex research queries
4. **Memory Usage**: Large crawl operations may consume significant memory

### Debug Tips
- Monitor crawl activity through the built-in activity callback
- Check API key validity and quota limits
- Adjust `maxDepth` and `maxUrls` for optimal performance
- Review network connectivity for web crawling operations

## Performance Optimization

### Crawl Efficiency
- **Depth Management**: Balance crawl depth with performance needs
- **URL Limits**: Set appropriate maximum URL limits based on research scope
- **Time Constraints**: Configure reasonable time limits to prevent long-running operations

### Resource Management
- **Memory Usage**: Monitor memory consumption during large crawl operations
- **API Quotas**: Track API usage to avoid exceeding rate limits
- **Network Bandwidth**: Consider bandwidth requirements for extensive crawling

## Contributing

1. Test with various research queries and domains
2. Optimize crawl parameters for different use cases
3. Enhance analysis prompts for specific industries
4. Add support for additional output formats

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Firecrawl](https://github.com/mendableai/firecrawl)
- [Firecrawl Documentation](https://github.com/mendableai/firecrawl)