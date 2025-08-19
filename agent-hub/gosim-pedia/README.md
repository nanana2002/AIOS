# GoSim-Pedia Node

A sophisticated MOFA node that creates comprehensive speaker biographies by aggregating information from multiple sources. This node specializes in generating detailed, well-structured biographies for speakers, professionals, and public figures using AI-powered analysis and multi-source data integration.

## Features

- **Multi-Source Data Aggregation**: Combines information from web search, web crawling, RAG systems, and social media
- **AI-Powered Analysis**: Uses advanced LLM capabilities to extract and structure speaker information
- **Comprehensive Biography Generation**: Creates detailed speaker profiles with chronological career paths
- **Social Media Integration**: Automatically searches for and includes social media presence
- **Structured Output**: Generates markdown-formatted biographies with rich metadata
- **Multimedia Content**: Includes images, videos, blogs, and publication links

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
LLM_BASE_URL=https://api.openai.com/v1  # optional, for custom endpoints
LLM_MODEL_NAME=gpt-4o  # optional, defaults to gpt-4o

# Alternative OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here  # alternative to LLM_API_KEY
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Speaker name or brief description to research |
| `firecrawl_result` | JSON | Yes | Web crawling results from Firecrawl agent |
| `serper_result` | JSON | Yes | Search results from Serper search agent |
| `rag_result` | JSON | Yes | RAG system results from GoSim-RAG agent |
| `firecrawl_link_result` | JSON | Yes | Social media and link crawling results |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `speaker_query` | string | Processed speaker name and organization for targeted search |
| `speaker_link_query` | string | Specialized query for finding speaker's social media and online presence |
| `speaker_summary` | string | Comprehensive markdown-formatted speaker biography |

## Usage Example

### Basic Dataflow Configuration

```yaml
# gosim-pedia-dataflow.yml
nodes:
  - id: dora-openai-server
    build: pip install -e ../../node-hub/dora-openai-server
    path: dora-openai-server
    outputs:
      - v1/chat/completions
    inputs:
       v1/chat/completions: gosim-pedia-agent/speaker_summary

  - id: gosim-pedia-agent
    build: pip install -e ../../agent-hub/gosim-pedia
    path: gosim-pedia
    outputs:
      - speaker_query
      - speaker_link_query
      - speaker_summary
    inputs:
      query: dora-openai-server/v1/chat/completions
      firecrawl_result: firecrawl-agent/firecrawl_agent_result
      serper_result: serper-search-agent/serper_result
      rag_result: gosim-rag-agent/gosim_rag_result
      firecrawl_link_result: firecrawl-link-agent/firecrawl_agent_result
    env:
      WRITE_LOG: true

  - id: firecrawl-agent
    build: pip install -e ../../agent-hub/firecrawl-agent
    path: firecrawl-agent
    outputs:
      - firecrawl_agent_result
    inputs:
      query: gosim-pedia-agent/speaker_query
    env:
      WRITE_LOG: true

  - id: serper-search-agent
    build: pip install -e ../../agent-hub/serper-search
    path: serper-search
    outputs:
      - serper_result
    inputs:
      query: gosim-pedia-agent/speaker_query
    env:
      WRITE_LOG: true

  - id: gosim-rag-agent
    build: pip install -e ../../agent-hub/gosim-rag
    path: gosim-rag
    outputs:
      - gosim_rag_result
    inputs:
      query: gosim-pedia-agent/speaker_query
    env:
      WRITE_LOG: true
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "LLM_API_KEY=your_openai_api_key" > .env.secret
   echo "LLM_MODEL_NAME=gpt-4o" >> .env.secret
   ```

2. **Start the MOFA framework:**
   ```bash
   dora up
   ```

3. **Build and start the dataflow:**
   ```bash
   dora build gosim-pedia-dataflow.yml
   dora start gosim-pedia-dataflow.yml
   ```

4. **Send speaker research queries:**
   Examples:
   - "Dr. Jane Smith, AI researcher at MIT"
   - "John Doe, CEO of TechCorp"
   - "Prof. Maria Garcia, quantum computing expert"

## Code Example

The core functionality is implemented in `main.py`:

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from openai import OpenAI
import json
from dotenv import load_dotenv

@run_agent
def run(agent: MofaAgent):
    env_file = '.env.secret'
    load_dotenv(env_file)
    query = agent.receive_parameter('query')
    
    # Create OpenAI client
    llm_client = create_openai_client()
    
    # Extract speaker information
    speaker_info = get_llm_response(
        client=llm_client, 
        messages=[
            {"role": "system", "content": extract_speaker_prompt},
            {"role": "user", "content": query},
        ]
    )
    
    # Process speaker information
    speaker_info_data = json.loads(speaker_info.replace('\n', '').replace('```json', '').replace('\n```', '').replace('```', ''))
    speaker_name_and_organization = speaker_info_data.get('name') + ' - ' + speaker_info_data.get('organization')
    
    # Send targeted search queries
    agent.send_output(agent_output_name='speaker_query', agent_result=speaker_name_and_organization)
    
    # Generate specialized social media search query
    speaker_link_search = f'"{speaker_info_data.get("name")}" ({speaker_info_data.get("organization")}) (site:github.com OR site:linkedin.com OR site:twitter.com OR site:x.com)'
    agent.send_output(agent_output_name='speaker_link_query', agent_result=speaker_link_search)
    
    # Receive results from other agents
    tool_results = agent.receive_parameters([
        'firecrawl_result', 'serper_result', 'rag_result', 'firecrawl_link_result'
    ])
    
    # Generate comprehensive biography
    summary_messages = [
        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": 'firecrawl_result: ' + json.dumps(tool_results.get('firecrawl_result'))},
        {"role": "user", "content": 'serper_result: ' + json.dumps(tool_results.get('serper_result'))},
        {"role": "user", "content": 'rag_result : ' + json.dumps(tool_results.get('rag_result'))},
        {"role": "user", "content": 'firecrawl_link_result : ' + json.dumps(tool_results.get('firecrawl_link_result'))},
    ]
    
    summary_speaker_info = get_llm_response(client=llm_client, messages=summary_messages)
    agent.send_output('speaker_summary', summary_speaker_info)
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **openai**: For OpenAI API integration (needs to be added to pyproject.toml)
- **python-dotenv**: For environment variable management (needs to be added to pyproject.toml)
- **mofa**: MOFA framework (automatically available in MOFA environment)

**Note**: This node requires `openai` and `python-dotenv` which should be added to `pyproject.toml`.

## Key Features

### Information Extraction
- **Speaker Profiling**: Extracts name, organization, keywords, and career journey from input
- **Multi-Source Integration**: Combines data from web crawling, search engines, and RAG systems
- **Social Media Discovery**: Automatically generates targeted queries for social media presence
- **Structured Processing**: Converts unstructured data into organized biographical information

### Biography Generation
- **Comprehensive Sections**: Includes personal info, career path, publications, awards, and more
- **Chronological Organization**: Presents information in timeline format for clarity
- **Rich Media Integration**: Incorporates images, videos, blogs, and publication links
- **Professional Formatting**: Generates clean markdown with proper sectioning and citations

### Multi-Agent Coordination
- **Query Distribution**: Sends specialized queries to different research agents
- **Result Aggregation**: Collects and synthesizes results from multiple sources
- **Intelligent Orchestration**: Coordinates between firecrawl, serper, and RAG agents
- **Output Optimization**: Combines all data sources for comprehensive biographical coverage

## Biography Sections

The generated biography includes the following comprehensive sections:

### Core Information
- **Personal Information**: Full name, current position, education, location
- **Career Path**: Chronological timeline of professional positions and achievements
- **Role Description**: Overview of current position and key responsibilities

### Professional Details  
- **Major Contributions**: Significant achievements and innovations in their field
- **Publications**: List of notable publications with descriptions and links
- **Awards and Recognitions**: Honors and awards received throughout career
- **Media Appearances**: Interviews, podcasts, and media coverage

### Personal Insights
- **Biography**: Professional background and career journey
- **Personal Insights**: Anecdotes and reflections on their professional journey
- **Influence and Impact**: Description of their influence in their field or industry

### Digital Presence
- **Social Media Presence**: Links to Twitter, LinkedIn, GitHub, personal websites
- **Public Engagements**: Conference talks, webinars, and speaking engagements
- **Multimedia Content**: Images, videos, and blog posts with proper citations

## Use Cases

### Event Management
- **Speaker Profiles**: Generate comprehensive profiles for conference speakers
- **Panel Preparation**: Create detailed backgrounds for panel discussants
- **Introduction Materials**: Provide rich content for speaker introductions
- **Marketing Content**: Generate promotional content highlighting speaker expertise

### Academic Research
- **Researcher Profiles**: Compile detailed academic biographies for collaboration
- **Citation Analysis**: Track publications and research contributions
- **Network Mapping**: Understand academic connections and collaborations
- **Impact Assessment**: Evaluate researcher influence and contributions

### Business Intelligence
- **Executive Profiling**: Research business leaders and decision makers
- **Partnership Evaluation**: Assess potential collaborators and partners
- **Industry Analysis**: Understand key players in specific sectors
- **Due Diligence**: Comprehensive background research for business decisions

### Media and Journalism
- **Interview Preparation**: Gather comprehensive background for interviews
- **Profile Articles**: Generate detailed profiles for feature stories
- **Expert Sourcing**: Identify and research subject matter experts
- **Fact Verification**: Cross-reference information across multiple sources

## Advanced Configuration

### Custom Prompts
The node uses sophisticated prompts for information extraction and biography generation:

- **Extract Speaker Prompt**: Structured extraction of key speaker information
- **Summary Prompt**: Comprehensive biography compilation with 22 detailed sections
- **Professional Tone**: Maintains third-person perspective for professional biographies

### Integration Requirements
This node requires integration with multiple other MOFA agents:

- **Firecrawl Agent**: For web crawling and content extraction
- **Serper Search Agent**: For web search results and information gathering
- **GoSim-RAG Agent**: For RAG-based information retrieval
- **OpenAI Server**: For LLM processing and response generation

## Troubleshooting

### Common Issues
1. **API Key Errors**: Ensure OpenAI API key is valid and has sufficient quota
2. **Missing Dependencies**: Verify all required agents are properly configured
3. **Data Quality**: Ensure input sources provide sufficient biographical information
4. **Memory Usage**: Large biographical data sets may consume significant memory

### Debug Tips
- Enable detailed logging with `WRITE_LOG: true` environment variable
- Check API key validity and quota limits
- Verify all dependent agents are running and responsive
- Monitor data flow between interconnected agents

## Performance Optimization

### Processing Efficiency
- **Parallel Processing**: Multiple agents work concurrently to gather information
- **Targeted Queries**: Specialized queries optimize information retrieval
- **Data Filtering**: Intelligent filtering reduces processing overhead
- **Cache Utilization**: Reuse results where possible to improve performance

### Quality Assurance
- **Multi-Source Verification**: Cross-reference information across multiple sources
- **Structured Validation**: Validate data structure and completeness
- **Content Quality**: Ensure biographical accuracy and professional presentation
- **Link Verification**: Validate URLs and multimedia references

## Contributing

1. Test with various speaker types and domains
2. Enhance biography templates for specific industries
3. Improve social media discovery algorithms
4. Add support for additional data sources and formats

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://mofa.ai/)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
