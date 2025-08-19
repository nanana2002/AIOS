# Agent Code Generator 节点

一个复杂的 MOFA 节点，使用 AI 自动为 dora-rs 框架生成符合规范的 Python 代理代码。该节点利用大语言模型根据用户规范和配置创建结构化的、生产就绪的代理代码。

## 功能特性

- **AI 驱动的代码生成**：使用 LLM 生成完整的 MOFA 代理代码
- **结构化输出**：利用 Pydantic 模型确保代码结构一致
- **配置驱动**：解析代理配置以定制代码生成
- **文件系统集成**：自动创建目录结构和文件
- **模板合规性**：生成严格遵循 dora-rs 框架标准的代码
- **错误处理**：在生成的代码中包含全面的错误控制

## 安装

以开发模式安装包：

```bash
pip install -e .
```

**注意**：该节点需要额外的依赖项，应添加到 `pyproject.toml` 中：
- `openai` - 用于 AI 代码生成
- `python-dotenv` - 用于环境变量管理
- `pydantic` - 用于结构化数据模型

## 配置

该节点使用综合配置系统：

### 代理配置 (`configs/agent.yml`)
包含 AI 代码生成器的详细提示和模板，包括：
- 框架合规性要求
- 代码结构模板
- 实现模式
- 合规性检查表

### 环境配置 (`.env.secret`)
LLM API 访问所需（出于安全考虑未包含在存储库中）。

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `query` | string | 是 | 要生成的代理的用户规范 |
| `agent_config` | string (JSON) | 是 | 包含 agent_name 和 module_name 的配置对象 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `code_generator_result` | string (JSON) | 生成的代理信息，包括代码和元数据 |

## 使用示例

### 基本数据流配置

```yaml
# agent_code_generator_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      agent_response: agent-code-generator/code_generator_result
  - id: agent-code-generator
    build: pip install -e ../../agent-hub/agent-code-generator
    path: agent-code-generator
    outputs:
      - code_generator_result
    inputs:
      query: terminal-input/data
      agent_config: terminal-input/agent_config
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
   dora build agent_code_generator_dataflow.yml
   dora start agent_code_generator_dataflow.yml
   ```

3. **发送输入数据：**
   提供用户查询和代理配置 JSON 以生成代理代码。

## 代码示例

核心功能在 `main.py` 中实现：

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from pydantic import BaseModel, Field

class AgentInfo(BaseModel):
    creation_time: str = Field(..., description="代理的创建时间。")
    llm_generated_code: str = Field(..., description="LLM 生成的 Python 代码。")
    description: Optional[str] = Field(None, description="代理的可选描述。")

@run_agent
def run(agent: MofaAgent):
    env_file_path = os.path.join(agent_config_dir_path, '.env.secret')
    agent_config_path = os.path.join(agent_config_dir_path, 'configs', 'agent.yml')
    
    # 接收参数
    receive_data = agent.receive_parameters(['query', 'agent_config'])
    agent_name = json.loads(receive_data.get('agent_config')).get('agent_name')
    
    # 使用 LLM 生成代码
    user_query = f"user q: {receive_data.get('query')}  /n agent config: {receive_data.get('agent_config')}"
    result = generate_agent_config(response_model=AgentInfo, user_query=user_query, 
                                 agent_config_path=agent_config_path, env_file_path=env_file_path)
    
    # 如果提供了 agent_name 则创建文件
    if agent_name:
        make_dir(f"{agent_name}/{module_name}")
        write_file(data=result.llm_generated_code, file_path=f"{agent_name}/{module_name}/main.py")
    
    agent.send_output(agent_output_name='code_generator_result', agent_result=result.json())
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **openai**：用于 LLM API 集成（需要添加到 pyproject.toml）
- **python-dotenv**：用于环境变量管理（需要添加到 pyproject.toml）
- **pydantic**：用于结构化数据模型（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

## 生成代码特性

AI 生成器创建的代理具有：
- **框架合规性**：严格遵循 dora-rs 标准
- **MofaAgent 基类**：正确的继承和装饰
- **输入/输出处理**：正确的参数接收和输出发送
- **错误处理**：全面的错误控制
- **类型安全**：适当的类型转换和序列化
- **文档**：清晰的代码结构和注释

## 使用场景

- **快速代理开发**：快速生成样板代理代码
- **框架合规性**：确保生成的代理遵循 dora-rs 标准
- **代码模板**：创建标准化的代理模式
- **开发自动化**：自动化重复的代理创建任务
- **教育工具**：学习正确的 MOFA 代理结构

## 贡献

1. 确保您的代码遵循现有风格
2. 将缺失的依赖项添加到 pyproject.toml
3. 根据需要更新文档
4. 使用各种生成场景进行测试

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://github.com/moxin-org/mofa)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)