# GoSim-RAG Node

A MOFA node that provides Retrieval-Augmented Generation (RAG) capabilities using vector search and embeddings. This node specializes in retrieving relevant information from a pre-built vector database using semantic similarity search, making it ideal for knowledge retrieval and context-aware information lookup.

## Features

- **Vector Database Integration**: Uses ChromaDB for efficient vector storage and retrieval
- **Embedding-Based Search**: Utilizes advanced embedding models for semantic similarity matching
- **Configurable Search Parameters**: Customizable search depth and embedding model selection
- **High-Performance Retrieval**: Optimized vector search with configurable result limits
- **Flexible Embedding Support**: Compatible with various embedding models including OpenAI's text-embedding-3-large
- **Environment-Driven Configuration**: Easy configuration through environment variables

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

### Environment Configuration (`.env.secret`)
Required environment variables:

```bash
# Embedding API Configuration
EMBEDDING_API_KEY=your_openai_api_key_here  # OpenAI API key for embeddings
EMBEDDING_MODEL_NAME=text-embedding-3-large  # Optional, default: text-embedding-3-large

# Vector Database Configuration
VECTOR_CHROME_PATH=chroma_store  # Optional, path to ChromaDB storage (default: chroma_store)
VECTOR_SEARCH_NUM=12            # Optional, number of search results to return (default: 12)
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The search query to find relevant information in the vector database |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `gosim_rag_result` | string | Retrieved relevant documents/chunks from the vector database |

## Usage Example

### Integration with GoSim-Pedia

This node is typically used as part of a larger data flow, such as in the GoSim-Pedia system:

```yaml
# gosim-pedia-dataflow.yml (excerpt)
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

### Standalone Usage

```yaml
# simple-rag-dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      gosim_rag_result: gosim-rag-agent/gosim_rag_result

  - id: gosim-rag-agent
    build: pip install -e ../../agent-hub/gosim-rag
    path: gosim-rag
    outputs:
      - gosim_rag_result
    inputs:
      query: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "EMBEDDING_API_KEY=your_openai_api_key" > .env.secret
   echo "EMBEDDING_MODEL_NAME=text-embedding-3-large" >> .env.secret
   echo "VECTOR_CHROME_PATH=./chroma_store" >> .env.secret
   echo "VECTOR_SEARCH_NUM=12" >> .env.secret
   ```

2. **Ensure vector database exists:**
   Make sure you have a pre-built ChromaDB vector store at the specified path with your documents indexed.

3. **Start the MOFA framework:**
   ```bash
   dora up
   ```

4. **Build and start the dataflow:**
   ```bash
   dora build simple-rag-dataflow.yml
   dora start simple-rag-dataflow.yml
   ```

5. **Send search queries:**
   Examples:
   - "artificial intelligence research"
   - "machine learning applications"
   - "data science methodologies"

## Code Example

The core functionality is implemented in `main.py`:

```python
import os
from dotenv import load_dotenv
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from mofa.kernel.rag.embedding.huggingface import load_embedding_model
from mofa.kernel.rag.vector.util import search_vector
from mofa.utils.database.vector.chromadb import create_chroma_db_conn_with_langchain

@run_agent
def run(agent: MofaAgent):
    env_file = '.env.secret'
    load_dotenv(env_file)
    
    # Configuration
    chroma_path = os.getenv('VECTOR_CHROME_PATH', 'chroma_store')
    model_name = os.getenv('EMBEDDING_MODEL_NAME', 'text-embedding-3-large')
    search_num = os.getenv('VECTOR_SEARCH_NUM', 12)
    
    # Set up embedding API key
    os.environ["OPENAI_API_KEY"] = os.getenv('EMBEDDING_API_KEY')
    
    # Initialize embedding model and vector store
    embedding = load_embedding_model(model_name=model_name)
    vectorstore = create_chroma_db_conn_with_langchain(
        embedding=embedding, 
        db_path=chroma_path
    )
    
    # Receive query and perform vector search
    query = agent.receive_parameter('query')
    vector_results = search_vector(
        vectorstore=vectorstore, 
        keywords=[query], 
        k=search_num
    )
    
    # Send results
    agent.send_output(
        agent_output_name='gosim_rag_result',
        agent_result=vector_results
    )

def main():
    agent = MofaAgent(agent_name='gosim-rag-agent')
    run(agent=agent)
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **chromadb**: For vector database operations (needs to be added to pyproject.toml)
- **langchain**: For vector store integration (needs to be added to pyproject.toml)
- **openai**: For embedding model API calls (needs to be added to pyproject.toml)
- **python-dotenv**: For environment variable management (needs to be added to pyproject.toml)
- **mofa**: MOFA framework (automatically available in MOFA environment)

**Note**: This node requires several dependencies that should be added to `pyproject.toml`:
- `chromadb`
- `langchain`
- `openai` 
- `python-dotenv`

## Key Features

### Vector Search Capabilities
- **Semantic Similarity**: Uses embedding-based search for semantic rather than keyword matching
- **Configurable Results**: Adjustable number of results returned (default: 12)
- **High Performance**: Optimized vector operations for fast retrieval
- **Relevance Ranking**: Results automatically ranked by similarity score

### Embedding Model Support
- **Multiple Models**: Support for various embedding models including OpenAI's latest
- **Flexible Configuration**: Easy switching between different embedding providers
- **API Integration**: Seamless integration with embedding service APIs
- **Model Optimization**: Efficient model loading and caching

### Database Integration
- **ChromaDB Backend**: Reliable and performant vector database
- **Persistent Storage**: Vector data persisted across sessions
- **Scalable Architecture**: Handles large document collections efficiently
- **LangChain Integration**: Leverages LangChain for vector store operations

## Use Cases

### Knowledge Base Search
- **Document Retrieval**: Find relevant documents from large collections
- **FAQ Systems**: Retrieve answers to frequently asked questions
- **Technical Documentation**: Search through technical manuals and guides
- **Research Papers**: Find relevant academic papers and publications

### Contextual Information Retrieval
- **Speaker Research**: Retrieve background information for biography generation
- **Topic Exploration**: Find related content for topic analysis
- **Content Augmentation**: Enhance responses with relevant context
- **Information Synthesis**: Gather supporting information for comprehensive analysis

### AI-Powered Applications
- **Chatbot Enhancement**: Provide context for conversational AI systems
- **Content Generation**: Supply relevant information for content creation
- **Question Answering**: Support QA systems with relevant knowledge
- **Recommendation Systems**: Find similar or related content

## Configuration Options

### Vector Database Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `VECTOR_CHROME_PATH` | `chroma_store` | Path to ChromaDB storage directory |
| `VECTOR_SEARCH_NUM` | `12` | Number of search results to return |

### Embedding Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EMBEDDING_MODEL_NAME` | `text-embedding-3-large` | Embedding model to use |
| `EMBEDDING_API_KEY` | Required | API key for embedding service |

### Advanced Configuration

```bash
# High-precision search with more results
VECTOR_SEARCH_NUM=20
EMBEDDING_MODEL_NAME=text-embedding-3-large

# Performance-optimized settings
VECTOR_SEARCH_NUM=5
EMBEDDING_MODEL_NAME=text-embedding-3-small
```

## Vector Database Setup

### Prerequisites
Before using this node, you need to:

1. **Create Vector Database**: Build a ChromaDB vector store with your documents
2. **Generate Embeddings**: Process your documents through an embedding model
3. **Store Vectors**: Save the embeddings in ChromaDB format

### Example Database Creation
```python
from mofa.kernel.rag.embedding.huggingface import load_embedding_model
from mofa.utils.database.vector.chromadb import create_chroma_db_conn_with_langchain

# Load embedding model
embedding = load_embedding_model(model_name='text-embedding-3-large')

# Create vector store
vectorstore = create_chroma_db_conn_with_langchain(
    embedding=embedding, 
    db_path='./chroma_store'
)

# Add documents (example)
documents = ["Document 1 content...", "Document 2 content..."]
vectorstore.add_texts(documents)
```

## Troubleshooting

### Common Issues
1. **Missing Vector Database**: Ensure ChromaDB store exists at specified path
2. **API Key Errors**: Verify embedding API key is valid and has sufficient quota
3. **Model Loading Errors**: Check embedding model name and availability
4. **Search Returns Empty**: Verify database contains indexed documents

### Debug Tips
- Check vector database path exists and contains data
- Verify embedding API key and quota limits
- Test embedding model loading independently
- Monitor search performance and adjust result count
- Enable detailed logging with `WRITE_LOG: true`

## Performance Optimization

### Search Performance
- **Result Limiting**: Adjust `VECTOR_SEARCH_NUM` based on needs vs. performance
- **Model Selection**: Use appropriate embedding model for your use case
- **Database Optimization**: Ensure ChromaDB is properly indexed
- **Caching**: Leverage embedding model caching for repeated queries

### Resource Management
- **Memory Usage**: Monitor memory consumption with large vector databases
- **API Calls**: Optimize embedding API usage to manage costs
- **Storage Space**: Monitor ChromaDB storage requirements
- **Processing Time**: Balance search depth with response time requirements

## Integration Patterns

### With Other MOFA Agents
This node is commonly used in conjunction with:
- **GoSim-Pedia**: Provides context for speaker biography generation
- **Search Agents**: Supplements web search with local knowledge
- **Content Generation**: Supplies context for AI content creation
- **Analysis Agents**: Provides background information for analysis tasks

### Data Flow Patterns
```yaml
# Typical integration pattern
Search Query -> RAG Retrieval -> Context Enhancement -> Final Output
```

## Contributing

1. Test with various vector database sizes and configurations
2. Optimize search algorithms for specific use cases
3. Add support for additional embedding models and providers
4. Enhance integration with other vector database backends

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://mofa.ai/)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [ChromaDB](https://www.trychroma.com/)
- [LangChain](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
