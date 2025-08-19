# Agent Config Generator 节点

一个智能的 MOFA 节点，使用 AI 自动分析代码并为代理生成全面的配置文件。该节点采用两阶段生成流程来创建项目标识符和配置内容，智能区分敏感和常规配置数据。

## 功能特性

- **AI 驱动的配置分析**：使用 LLM 分析代码并检测配置需求
- **两阶段生成流程**：先生成项目标识符（agent_name, module_name），再生成配置内容
- **智能敏感信息检测**：自动区分敏感信息（.env.secret）和常规配置（.yml）
- **文件系统集成**：自动创建目录结构并写入配置文件
- **智能命名规范**：遵循 PascalCase 代理名称和 snake_case 模块名称
- **安全最佳实践**：为敏感数据使用占位符值并维护安全协议

## 安装

以开发模式安装包：

```bash
pip install -e .
```

**注意**：该节点需要额外的依赖项，应添加到 `pyproject.toml` 中：
- `pydantic` - 用于结构化数据模型
- LLM 集成可能需要其他依赖项

## 配置

该节点使用具有两个专门提示的高级配置系统：

### 代理配置 (`configs/agent.yml`)
包含两个主要提示部分：

#### 1. 主配置生成提示 (`prompt`)
- 检测敏感信息（keys、secrets、tokens、passwords）
- 识别常规配置参数
- 生成适当的 .env 和 .yml 结构
- 应用安全最佳实践

#### 2. 项目标识符生成提示 (`agent_name_gen_prompt`)
- 从用户需求中派生技术标识符
- 遵循严格的命名规范（代理使用 PascalCase，模块使用 snake_case）
- 处理冲突解决和验证
- 确保生成名称的语义含义

### 环境配置 (`.env.secret`)
LLM API 访问所需（出于安全考虑未包含在存储库中）。

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `query` | string | 是 | 要分析的用户规范或代码，用于配置生成 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `config_generator_result` | object | 生成的配置数据，包括 agent_name、module_name、env_config 和 yml_config |

## 使用示例

### 基本数据流配置

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

### 运行节点

1. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

2. **构建并启动数据流：**
   ```bash
   dora build agent_config_generator_dataflow.yml
   dora start agent_config_generator_dataflow.yml
   ```

3. **发送输入数据：**
   提供代码或需求进行分析和配置生成。

## 代码示例

核心功能在 `main.py` 中实现：

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from pydantic import BaseModel, Field

class LLMGeneratedConfig(BaseModel):
    agent_name: str = Field(..., description="代理的名称。")
    module_name: str = Field(..., description="模块的名称。")

class LLMGeneratedContent(BaseModel):
    env_config: Optional[str] = Field(None, description="生成的 .env 配置内容")
    yml_config: Optional[str] = Field(None, description="生成的 YAML 配置内容")

@run_agent
def run(agent: MofaAgent):
    env_file_path = os.path.join(agent_config_dir_path, '.env.secret')
    agent_config_path = os.path.join(agent_config_dir_path, 'configs', 'agent.yml')
    user_query = agent.receive_parameter('query')
    
    # 第一阶段：生成项目标识符
    config_result = generate_agent_config(
        response_model=LLMGeneratedConfig, 
        user_query=user_query, 
        agent_config_path=agent_config_path, 
        env_file_path=env_file_path,
        prompt_selection='agent_name_gen_prompt'
    )
    
    # 创建目录结构
    agent_name = config_result.agent_name.replace(' ', '-').replace('_', '-')
    module_name = config_result.module_name.replace(' ', '_').lower()
    make_dir(f"{agent_name}/{module_name}/configs")
    
    # 第二阶段：生成配置内容
    result = generate_agent_config(
        response_model=LLMGeneratedContent, 
        user_query=user_query, 
        agent_config_path=agent_config_path, 
        env_file_path=env_file_path,
        add_prompt=f"agent_name: {agent_name} module_name: {module_name}"
    )
    
    # 写入配置文件
    write_file(data=result.yml_config, file_path=f"{agent_name}/{module_name}/configs/agent.yml")
    write_file(data=result.env_config, file_path=f"{agent_name}/{module_name}/.env.secret")
    
    agent.send_output(agent_output_name='config_generator_result', agent_result=result_dict)
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **pydantic**：用于结构化数据模型（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

## 配置检测规则

### 敏感信息检测
- 包含以下内容的变量名：`key`、`secret`、`token`、`password`、`credential`
- 在身份验证或加密上下文中的使用
- 生成带有占位符值的 `.env.secret` 文件

### 常规配置检测
- 包含以下内容的变量名：`config`、`setting`、`param`
- 功能开关或参数调整
- 非敏感的操作参数
- 生成带有合理默认值的 `.yml` 文件

### 命名规范规则
- **代理名称**：PascalCase 格式（例如：`PDFProcessor`、`DataAnalysisTool`）
- **模块名称**：snake_case 格式（例如：`pdf_processor`、`data_analyzer`）
- 使用正则表达式模式进行长度和格式验证

## 使用场景

- **自动配置设置**：为新代理生成配置文件
- **代码分析和结构**：分析现有代码以提取配置需求
- **安全合规**：确保敏感和常规配置的正确分离
- **项目脚手架**：创建适当的目录结构和配置模板
- **开发自动化**：简化代理开发工作流程

## 贡献

1. 确保您的代码遵循现有风格
2. 将缺失的依赖项添加到 pyproject.toml
3. 使用各种代码分析场景进行测试
4. 根据需要更新文档

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://github.com/moxin-org/mofa)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)