# Agent Config Generator Node

An intelligent MOFA node that uses AI to automatically analyze code and generate comprehensive configuration files for agents. This node employs a two-stage generation process to create both project identifiers and configuration content, intelligently distinguishing between sensitive and regular configuration data.

## Features

- **AI-Powered Configuration Analysis**: Uses LLM to analyze code and detect configuration requirements
- **Two-Stage Generation Process**: First generates project identifiers (agent_name, module_name), then configuration content
- **Intelligent Sensitivity Detection**: Automatically distinguishes between sensitive (.env.secret) and regular (.yml) configurations
- **File System Integration**: Automatically creates directory structures and writes configuration files
- **Smart Naming Convention**: Follows PascalCase for agent names and snake_case for module names
- **Security Best Practices**: Uses placeholder values for sensitive data and maintains security protocols

## Installation

Install the package in development mode:

```bash
pip install -e .
```

**Note**: This node requires additional dependencies that should be added to `pyproject.toml`:
- `pydantic` - for structured data models
- Additional dependencies may be required for LLM integration

## Configuration

This node uses an advanced configuration system with two specialized prompts:

### Agent Configuration (`configs/agent.yml`)
Contains two main prompt sections:

#### 1. Main Configuration Generation Prompt (`prompt`)
- Detects sensitive information (keys, secrets, tokens, passwords)
- Identifies regular configuration parameters
- Generates appropriate .env and .yml structures
- Applies security best practices

#### 2. Project Identifier Generation Prompt (`agent_name_gen_prompt`)
- Derives technical identifiers from user requirements
- Follows strict naming conventions (PascalCase for agents, snake_case for modules)
- Handles conflict resolution and validation
- Ensures semantic meaning in generated names

### Environment Configuration (`.env.secret`)
Required for LLM API access (not included in repository for security).

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | User specification or code to analyze for configuration generation |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `config_generator_result` | object | Generated configuration data including agent_name, module_name, env_config, and yml_config |

## Usage Example

### Basic Dataflow Configuration

```yaml
# agent_config_generator_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      agent_response: agent-config-generator/config_generator_result
  - id: agent-config-generator
    build: pip install -e ../../agent-hub/agent-config-generator
    path: agent-config-generator
    outputs:
      - config_generator_result
    inputs:
      query: terminal-input/data
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
   dora build agent_config_generator_dataflow.yml
   dora start agent_config_generator_dataflow.yml
   ```

3. **Send input data:**
   Provide code or requirements for analysis and configuration generation.

## Code Example

The core functionality is implemented in `main.py`:

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from pydantic import BaseModel, Field

class LLMGeneratedConfig(BaseModel):
    agent_name: str = Field(..., description="The name of the agent.")
    module_name: str = Field(..., description="The name of the module.")

class LLMGeneratedContent(BaseModel):
    env_config: Optional[str] = Field(None, description="Generated .env configuration content")
    yml_config: Optional[str] = Field(None, description="Generated YAML configuration content")

@run_agent
def run(agent: MofaAgent):
    env_file_path = os.path.join(agent_config_dir_path, '.env.secret')
    agent_config_path = os.path.join(agent_config_dir_path, 'configs', 'agent.yml')
    user_query = agent.receive_parameter('query')
    
    # Stage 1: Generate project identifiers
    config_result = generate_agent_config(
        response_model=LLMGeneratedConfig, 
        user_query=user_query, 
        agent_config_path=agent_config_path, 
        env_file_path=env_file_path,
        prompt_selection='agent_name_gen_prompt'
    )
    
    # Create directory structure
    agent_name = config_result.agent_name.replace(' ', '-').replace('_', '-')
    module_name = config_result.module_name.replace(' ', '_').lower()
    make_dir(f"{agent_name}/{module_name}/configs")
    
    # Stage 2: Generate configuration content
    result = generate_agent_config(
        response_model=LLMGeneratedContent, 
        user_query=user_query, 
        agent_config_path=agent_config_path, 
        env_file_path=env_file_path,
        add_prompt=f"agent_name: {agent_name} module_name: {module_name}"
    )
    
    # Write configuration files
    write_file(data=result.yml_config, file_path=f"{agent_name}/{module_name}/configs/agent.yml")
    write_file(data=result.env_config, file_path=f"{agent_name}/{module_name}/.env.secret")
    
    agent.send_output(agent_output_name='config_generator_result', agent_result=result_dict)
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **pydantic**: For structured data models (needs to be added to pyproject.toml)
- **mofa**: MOFA framework (automatically available in MOFA environment)

## Configuration Detection Rules

### Sensitive Information Detection
- Variable names containing: `key`, `secret`, `token`, `password`, `credential`
- Usage in authentication or encryption contexts
- Generates `.env.secret` files with placeholder values

### Regular Configuration Detection
- Variable names containing: `config`, `setting`, `param`
- Feature toggles or parameter adjustments
- Non-sensitive operational parameters
- Generates `.yml` files with reasonable defaults

### Naming Convention Rules
- **Agent Name**: PascalCase format (e.g., `PDFProcessor`, `DataAnalysisTool`)
- **Module Name**: snake_case format (e.g., `pdf_processor`, `data_analyzer`)
- Length and format validation with regex patterns

## Use Cases

- **Automated Configuration Setup**: Generate configuration files for new agents
- **Code Analysis and Structure**: Analyze existing code to extract configuration requirements
- **Security Compliance**: Ensure proper separation of sensitive and regular configuration
- **Project Scaffolding**: Create proper directory structures and configuration templates
- **Development Automation**: Streamline the agent development workflow

## Contributing

1. Ensure your code follows the existing style
2. Add missing dependencies to pyproject.toml
3. Test with various code analysis scenarios
4. Update documentation as needed

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)