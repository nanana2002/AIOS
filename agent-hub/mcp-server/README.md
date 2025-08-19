
# MCP Server Node

A MOFA node that provides MCP (Model Context Protocol) server capabilities for exposing tools and functions as standardized services. This node enables the creation of MCP-compliant servers that can be accessed by LLM clients and other applications for tool execution and resource access.

## Features

- **Tool Registration**: Register and expose Python functions as MCP tools
- **MCP Protocol Compliance**: Full compatibility with the Model Context Protocol specification
- **Function Discovery**: Automatic tool discovery and metadata generation
- **Real-time Communication**: Built-in server capabilities for handling MCP requests
- **MOFA Integration**: Seamless integration with MOFA agent framework
- **Example Tools**: Pre-built mathematical functions for demonstration

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

### Input Parameters

This node operates as a server and doesn't require traditional input parameters. Instead, it:
- Registers tools automatically upon startup
- Listens for MCP protocol requests
- Responds to tool execution requests from MCP clients

### Available Tools

The node comes with example tools pre-registered:

| Tool | Parameters | Description |
|------|------------|-------------|
| `add` | `a: int, b: int` | Adds two numbers and returns the result |
| `multiply` | `a: int, b: int` | Multiplies two numbers (implemented as `a * add(a,b)`) |

## Usage Example

### Basic Dataflow Configuration

```yaml
# mcp-server-dataflow.yml
nodes:
  - id: mcp-server
    build: pip install -e ../../agent-hub/mcp-server
    path: mcp-server
    inputs:
      tick: dora/timer/millis/20
    env:
      MCP: true
```

### Running the Node

1. **Start the MOFA framework:**
   ```bash
   dora up
   ```

2. **Build and start the dataflow:**
   ```bash
   dora build mcp-server-dataflow.yml
   dora start mcp-server-dataflow.yml
   ```

3. **The server will start and display:**
   ```
   开始运行mcp服务
   ```

4. **Access the MCP server:**
   The server will be available for MCP client connections and tool execution requests.

## Code Example

The core functionality is implemented in `main.py`:

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent

def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * add(a, b)

@run_agent
def run(agent):
    # Register tools with the MCP server
    agent.register_mcp_tool(add)
    agent.register_mcp_tool(multiply)
    
    print('开始运行mcp服务')
    
    # Start the MCP server
    agent.run_mcp()

def main():
    agent_name = 'Mofa-Mcp'
    agent = MofaAgent(agent_name=agent_name)
    run(agent)
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **mcp**: For Model Context Protocol implementation
- **mofa**: MOFA framework (automatically available in MOFA environment)

## Key Features

### Tool Registration System
- **Function Decoration**: Automatic tool metadata extraction from Python functions
- **Type Safety**: Full support for typed function parameters and return values
- **Documentation Integration**: Function docstrings become tool descriptions
- **Dynamic Registration**: Tools can be registered at runtime

### MCP Protocol Implementation
- **Standards Compliance**: Fully implements the Model Context Protocol specification
- **Client Compatibility**: Works with any MCP-compliant client
- **Request Handling**: Efficient handling of tool discovery and execution requests
- **Error Management**: Proper error handling and response formatting

### Server Architecture
- **Asynchronous Operation**: Non-blocking server architecture
- **Concurrent Requests**: Handles multiple client requests simultaneously
- **Resource Management**: Efficient resource allocation and cleanup
- **Scalable Design**: Supports multiple tools and high request volumes

## MCP Protocol Overview

The Model Context Protocol (MCP) is a standard for exposing tools and resources to AI systems:

### Tool Discovery
```json
{
  "method": "tools/list",
  "params": {}
}
```

### Tool Execution
```json
{
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": {
      "a": 5,
      "b": 3
    }
  }
}
```

## Custom Tool Development

### Adding New Tools

```python
def divide(a: float, b: float) -> float:
    """Divide two numbers with error handling"""
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b

def get_system_info() -> dict:
    """Get system information"""
    import platform
    return {
        "system": platform.system(),
        "python_version": platform.python_version(),
        "machine": platform.machine()
    }

@run_agent
def run(agent):
    # Register existing tools
    agent.register_mcp_tool(add)
    agent.register_mcp_tool(multiply)
    
    # Register new custom tools
    agent.register_mcp_tool(divide)
    agent.register_mcp_tool(get_system_info)
    
    print('MCP server running with custom tools')
    agent.run_mcp()
```

### Tool Requirements
- Functions must have proper type hints for parameters
- Return types should be JSON-serializable
- Include comprehensive docstrings for tool descriptions
- Handle errors gracefully with appropriate exceptions

## Use Cases

### AI Assistant Integration
- **LLM Tool Access**: Provide tools for AI assistants to perform calculations
- **Function Libraries**: Expose utility functions to AI systems
- **Custom Capabilities**: Add domain-specific tools for specialized AI applications
- **Workflow Integration**: Enable AI systems to interact with business processes

### Microservices Architecture
- **Service Discovery**: Tools become discoverable services in distributed systems
- **API Standardization**: Consistent interface for accessing various functionalities
- **Interoperability**: Standard protocol for cross-service communication
- **Modularity**: Independent tool services with clear interfaces

### Development and Testing
- **Rapid Prototyping**: Quickly expose functions for testing and development
- **API Mocking**: Create mock services for testing AI integrations
- **Tool Validation**: Test tool implementations in controlled environments
- **Integration Testing**: Verify AI system interactions with tools

## Advanced Configuration

### Server Customization
```python
class CustomMCPAgent(MofaAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_custom_tools()
    
    def setup_custom_tools(self):
        # Register domain-specific tools
        self.register_mcp_tool(self.business_logic_tool)
        self.register_mcp_tool(self.data_processing_tool)
    
    def business_logic_tool(self, data: dict) -> dict:
        """Process business logic"""
        # Custom business logic implementation
        return {"processed": True, "result": data}
```

### Error Handling
```python
def safe_divide(a: float, b: float) -> dict:
    """Safely divide two numbers with error reporting"""
    try:
        if b == 0:
            return {"error": "Division by zero", "result": None}
        return {"error": None, "result": a / b}
    except Exception as e:
        return {"error": str(e), "result": None}
```

## Client Integration

### MCP Client Example
```python
import asyncio
from mcp_client import ClientSession

async def use_mcp_tools():
    async with ClientSession("stdio://mcp-server") as session:
        # Initialize connection
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        print("Available tools:", [tool.name for tool in tools])
        
        # Call a tool
        result = await session.call_tool("add", arguments={"a": 5, "b": 3})
        print("Addition result:", result)
        
        # Call another tool
        result = await session.call_tool("multiply", arguments={"a": 4, "b": 6})
        print("Multiplication result:", result)

# Run the client
asyncio.run(use_mcp_tools())
```

## Troubleshooting

### Common Issues
1. **Server Not Starting**: Check that MCP environment variable is set to true
2. **Tool Registration Errors**: Verify function type hints and docstrings
3. **Client Connection Issues**: Ensure server is running and accessible
4. **Tool Execution Failures**: Check function implementations and error handling

### Debug Tips
- Enable detailed logging to monitor tool registration and execution
- Test tools independently before registering them with MCP
- Verify MCP client compatibility and protocol version
- Monitor server performance under load

## Performance Considerations

### Scalability
- **Tool Complexity**: Keep tool implementations efficient to handle concurrent requests
- **Resource Usage**: Monitor memory and CPU usage under high load
- **Connection Management**: Implement proper connection pooling for multiple clients
- **Error Recovery**: Implement graceful handling of client disconnections

### Optimization
- **Caching**: Implement caching for expensive tool operations
- **Async Operations**: Use async/await patterns for I/O bound operations
- **Load Balancing**: Consider multiple server instances for high availability
- **Monitoring**: Implement metrics and monitoring for server health

## Contributing

1. Add new tools following the established patterns
2. Test tools thoroughly with various input types
3. Ensure proper error handling and documentation
4. Verify MCP protocol compliance for new features

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://mofa.ai/)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Model Context Protocol](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
