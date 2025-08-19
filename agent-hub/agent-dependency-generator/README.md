# Agent Dependency Generator Node

An intelligent MOFA node that uses AI to automatically generate Python package dependencies and documentation for agents. This node analyzes agent code and generates both `pyproject.toml` files with proper dependency detection and comprehensive `README.md` documentation following standardized templates.

## Features

- **AI-Powered Dependency Detection**: Automatically analyzes code to identify required Python packages
- **PyProject.toml Generation**: Creates Poetry-compatible configuration files with proper naming conventions
- **README Documentation**: Generates comprehensive GitHub-standard README files
- **Code Pattern Recognition**: Detects dependencies from code patterns (e.g., requests.get → requests package)
- **Template Compliance**: Follows strict TOML syntax validation and Poetry standards
- **Dual Output System**: Generates both technical dependencies and user-facing documentation

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

This node uses a sophisticated dual-prompt system:

### Agent Configuration (`configs/agent.yml`)
Contains two specialized prompts:

#### 1. PyProject Generation Prompt (`pyproject_prompt`)
- Follows Poetry packaging standards
- Automatically detects dependencies from code patterns
- Preserves user naming conventions (agent_name/module_name)
- Includes TOML syntax validation
- Generates MIT-licensed package configurations

#### 2. README Generation Prompt (`readme_prompt`) 
- Creates GitHub-standard README files
- Includes installation, usage, and API reference sections
- Generates integration examples and YAML configurations
- Supports Mermaid workflow diagrams for complex nodes
- Follows structured markdown formatting

### Environment Configuration (`.env.secret`)
Required for LLM API access (not included in repository for security).

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | User specification or requirements for the agent |
| `agent_config` | string (JSON) | Yes | Configuration object containing agent_name and module_name |
| `agent_code` | string (JSON) | Yes | Generated agent code containing llm_generated_code field |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dependency_generator_result` | string (JSON) | Generated TOML configuration data |

## Usage Example

### Basic Dataflow Configuration

```yaml
# agent_dependency_generator_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      agent_response: agent-dependency-generator/dependency_generator_result
  - id: agent-dependency-generator
    build: pip install -e ../../agent-hub/agent-dependency-generator
    path: agent-dependency-generator
    outputs:
      - dependency_generator_result
    inputs:
      query: terminal-input/data
      agent_config: terminal-input/agent_config
      agent_code: terminal-input/agent_code
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### Running the Node

1. **Start the MOFA framework:**
   ```bash
   dora up
   ```

2. **Build and start the dataflow:**
   ```bash
   dora build agent_dependency_generator_dataflow.yml
   dora start agent_dependency_generator_dataflow.yml
   ```

3. **Send input data:**
   Provide user query, agent configuration, and agent code for dependency and documentation generation.

## Code Example

The core functionality is implemented in `main.py`:

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from pydantic import BaseModel, Field
import toml

class LLMGeneratedTomlRequire(BaseModel):
    toml: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "PEP 621-compliant pyproject.toml configuration content"
        }
    )

class LLMGeneratedReadmeRequire(BaseModel):
    readme: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "GitHub-standard README content with installation and usage guidelines"
        }
    )

@run_agent
def run(agent: MofaAgent):
    env_file_path = os.path.join(agent_config_dir_path, '.env.secret')
    agent_config_path = os.path.join(agent_config_dir_path, 'configs', 'agent.yml')
    
    # Receive all required parameters
    receive_data = agent.receive_parameters(['query', 'agent_config', 'agent_code'])
    agent_name = json.loads(receive_data.get('agent_config')).get('agent_name')
    module_name = json.loads(receive_data.get('agent_config')).get('module_name')
    agent_code = json.loads(receive_data.get('agent_code')).get('llm_generated_code', '')
    
    # Generate pyproject.toml
    result = generate_agent_config(
        response_model=LLMGeneratedTomlRequire,
        user_query=receive_data.get('query'),
        agent_config_path=agent_config_path,
        env_file_path=env_file_path,
        add_prompt=f"agent_name: {agent_name} module_name: {module_name}",
        prompt_selection='pyproject_prompt'
    )
    
    # Generate README.md
    readme_result = generate_agent_config(
        response_model=LLMGeneratedReadmeRequire,
        user_query=str(agent_code),
        agent_config_path=agent_config_path,
        env_file_path=env_file_path,
        prompt_selection='readme_prompt',
        add_prompt=f"agent_name: {agent_name} module_name: {module_name}"
    )
    
    # Write files if agent_name provided
    if agent_name:
        make_dir(f"{agent_name}/{module_name}")
        write_file(data=readme_result.readme, file_path=f"{agent_name}/README.md")
        write_file(data=result.toml, file_path=f"{agent_name}/pyproject.toml")
    
    agent.send_output(agent_output_name='dependency_generator_result', agent_result=result.json())
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **toml**: For TOML file parsing and generation
- **pydantic**: For structured data models (used by mofa framework)
- **mofa**: MOFA framework (automatically available in MOFA environment)

## Generated PyProject.toml Features

### Automatic Dependency Detection
- **HTTP Libraries**: `requests.get()` → adds `requests = "*"`
- **Data Processing**: `pandas.DataFrame()` → adds `pandas = "*"`
- **Machine Learning**: `import torch` → adds `torch = "*"`
- **Web Frameworks**: `from fastapi import` → adds `fastapi = "*"`

### Template Structure
```toml
[tool.poetry]
name = "{agent_name}"
version = "0.1.0"
description = "Auto-generated agent package"
authors = ["Mofa Bot <mofa-bot@moxin.com>"]
packages = [{ include = "{module_name}" }]

[tool.poetry.dependencies]
python = ">=3.10"
pyarrow = ">= 5.0.0"
# Auto-detected dependencies based on code patterns

[tool.poetry.scripts]
{agent_name} = "{module_name}.main:main"
```

## Generated README Features

### Standard Sections
- Project description and tagline
- Feature list with bullet points
- Installation instructions
- Basic usage with YAML configuration examples
- Integration examples for connecting with other nodes
- API reference tables for input/output topics
- License information

### Advanced Features
- **Mermaid Diagrams**: Automatic workflow visualization for complex nodes
- **Integration Examples**: YAML configurations for connecting with other nodes
- **API Documentation**: Structured tables for input/output specifications
- **Metadata Examples**: JSON examples for proper data formatting

## Use Cases

- **Automated Package Creation**: Generate complete Python packages from agent code
- **Dependency Management**: Automatically detect and include required dependencies
- **Documentation Generation**: Create comprehensive README files for agent repositories
- **CI/CD Integration**: Generate files suitable for automated builds and deployments
- **Open Source Compliance**: Ensure proper licensing and attribution in generated packages

## Contributing

1. Ensure your code follows the existing style
2. Test dependency detection with various code patterns
3. Validate generated TOML files with `tomlkit.parse()`
4. Update documentation templates as needed

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Poetry Documentation](https://python-poetry.org/docs/)