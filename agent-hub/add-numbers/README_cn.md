# Add Numbers 节点

一个执行两个数字相加的 MOFA 节点。该节点接收两个数字输入并返回它们的和，展示了 MOFA 框架中的基本算术运算。

## 功能特性

- **加法运算**：将两个整数相加并返回和
- **MOFA 框架集成**：使用标准 MOFA 代理模式构建
- **参数批量处理**：使用 `receive_parameters` 高效处理多个输入
- **类型转换**：计算前自动将输入转换为整数
- **最小依赖**：轻量级实现，外部依赖最少

## 安装

以开发模式安装包：

```bash
pip install -e .
```

## 配置

该节点在 `configs/agent.yml` 包含基本代理配置文件。基本操作无需额外配置。

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `num1` | int | 是 | 要相加的第一个数字 |
| `num2` | int | 是 | 要相加的第二个数字 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `add_numbers_result` | int | num1 和 num2 的和 |

## 使用示例

### 基本数据流配置

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

### 运行节点

1. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

2. **构建并启动数据流：**
   ```bash
   dora build add_numbers_dataflow.yml
   dora start add_numbers_dataflow.yml
   ```

3. **发送输入数据：**
   使用 terminal-input 发送数字数据，将由加法节点处理。

## 代码示例

核心功能在 `main.py` 中实现：

```python
from pathlib import Path
from mofa.agent_build.base.base_agent import MofaAgent
import os

def add_two_numbers(a: int, b: int):
    a, b = int(a), int(b)  # 转换为整数
    return a + b

def main():
    agent = MofaAgent(agent_name='add_numbers_agent')
    while True:
        # 批量接收多个参数
        parameters_data = agent.receive_parameters(parameter_names=['num2', 'num1'])
        print('parameters_data:', parameters_data)
        
        # 执行加法运算
        result = add_two_numbers(a=parameters_data['num1'], b=parameters_data['num2'])
        
        # 发送结果
        agent.send_output(agent_output_name='add_numbers_result', agent_result=result)
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

## 使用场景

- **基础算术**：在数据处理管道中执行加法运算
- **数学工作流**：作为更大数学计算图的组件
- **数据聚合**：从不同数据源汇总值
- **学习示例**：理解 MOFA 中的参数处理和批量处理

## 贡献

1. 确保您的代码遵循现有风格
2. 为新功能添加测试
3. 根据需要更新文档
4. 提交更改前运行测试

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://github.com/moxin-org/mofa)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)