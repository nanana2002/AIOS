# Add Numbers Node

A MOFA node that performs addition of two numbers. This node receives two numeric inputs and returns their sum, demonstrating basic arithmetic operations in the MOFA framework.

## Features

- **Addition Operation**: Adds two integer numbers and returns the sum
- **MOFA Framework Integration**: Built using the standard MOFA agent pattern
- **Parameter Batch Processing**: Uses `receive_parameters` to handle multiple inputs efficiently
- **Type Conversion**: Automatically converts inputs to integers before calculation
- **Minimal Dependencies**: Lightweight implementation with minimal external dependencies

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

This node includes a basic agent configuration file at `configs/agent.yml`. No additional configuration is required for basic operation.

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `num1` | int | Yes | First number to be added |
| `num2` | int | Yes | Second number to be added |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `add_numbers_result` | int | The sum of num1 and num2 |

## Usage Example

### Basic Dataflow Configuration

```yaml
# add_numbers_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      add_numbers_result: add-numbers/add_numbers_result
      multiply_numbers_result: multiply-numbers/multiply_numbers_result
  - id: multiply-numbers
    build: pip install -e ../../agent-hub/multiply-numbers
    path: multiply-numbers
    outputs:
      - multiply_numbers_result
    inputs:
      num1: terminal-input/data
    env:
      IS_DATAFLOW_END: false
      WRITE_LOG: true
  - id: add-numbers
    build: pip install -e ../../agent-hub/add-numbers
    path: add-numbers
    outputs:
      - add_numbers_result
    inputs:
      num1: terminal-input/data
      num2: multiply-numbers/multiply_numbers_result
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
   dora build add_numbers_dataflow.yml
   dora start add_numbers_dataflow.yml
   ```

3. **Send input data:**
   Use terminal-input to send numeric data that will be processed by the addition node.

## Code Example

The core functionality is implemented in `main.py`:

```python
from pathlib import Path
from mofa.agent_build.base.base_agent import MofaAgent
import os

def add_two_numbers(a: int, b: int):
    a, b = int(a), int(b)  # convert to int
    return a + b

def main():
    agent = MofaAgent(agent_name='add_numbers_agent')
    while True:
        # Batch receive multiple parameters
        parameters_data = agent.receive_parameters(parameter_names=['num2', 'num1'])
        print('parameters_data:', parameters_data)
        
        # Perform addition
        result = add_two_numbers(a=parameters_data['num1'], b=parameters_data['num2'])
        
        # Send result
        agent.send_output(agent_output_name='add_numbers_result', agent_result=result)
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **mofa**: MOFA framework (automatically available in MOFA environment)

## Use Cases

- **Basic Arithmetic**: Perform addition operations in data processing pipelines
- **Mathematical Workflows**: Component in larger mathematical computation graphs
- **Data Aggregation**: Sum values from different data sources
- **Learning Example**: Understand parameter handling and batch processing in MOFA

## Contributing

1. Ensure your code follows the existing style
2. Add tests for new functionality
3. Update documentation as needed
4. Run tests before submitting changes

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)