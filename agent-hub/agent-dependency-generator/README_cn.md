# Agent Dependency Generator 节点

一个智能的 MOFA 节点，使用 AI 自动为代理生成 Python 包依赖和文档。该节点分析代理代码并生成带有适当依赖检测的 `pyproject.toml` 文件和遵循标准化模板的综合 `README.md` 文档。

## 功能特性

- **AI 驱动的依赖检测**：自动分析代码以识别所需的 Python 包
- **PyProject.toml 生成**：创建符合 Poetry 规范的配置文件，遵循正确的命名约定
- **README 文档**：生成符合 GitHub 标准的综合 README 文件
- **代码模式识别**：从代码模式检测依赖（例如：requests.get → requests 包）
- **模板合规性**：遵循严格的 TOML 语法验证和 Poetry 标准
- **双输出系统**：生成技术依赖和面向用户的文档

## 安装

以开发模式安装包：

```bash
pip install -e .
```

## 配置

该节点使用复杂的双提示系统：

### 代理配置 (`configs/agent.yml`)
包含两个专门的提示：

#### 1. PyProject 生成提示 (`pyproject_prompt`)
- 遵循 Poetry 打包标准
- 自动从代码模式中检测依赖
- 保留用户命名约定（agent_name/module_name）
- 包含 TOML 语法验证
- 生成 MIT 许可的包配置

#### 2. README 生成提示 (`readme_prompt`)
- 创建符合 GitHub 标准的 README 文件
- 包含安装、使用和 API 参考部分
- 生成集成示例和 YAML 配置
- 支持复杂节点的 Mermaid 工作流图表
- 遵循结构化的 markdown 格式

### 环境配置 (`.env.secret`)
LLM API 访问所需（出于安全考虑未包含在存储库中）。

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `query` | string | 是 | 代理的用户规范或需求 |
| `agent_config` | string (JSON) | 是 | 包含 agent_name 和 module_name 的配置对象 |
| `agent_code` | string (JSON) | 是 | 包含 llm_generated_code 字段的生成代理代码 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `dependency_generator_result` | string (JSON) | 生成的 TOML 配置数据 |

## 使用示例

### 基本数据流配置

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

### 运行节点

1. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

2. **构建并启动数据流：**
   ```bash
   dora build agent_dependency_generator_dataflow.yml
   dora start agent_dependency_generator_dataflow.yml
   ```

3. **发送输入数据：**
   提供用户查询、代理配置和代理代码进行依赖和文档生成。

## 代码示例

核心功能在 `main.py` 中实现：

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from pydantic import BaseModel, Field
import toml

class LLMGeneratedTomlRequire(BaseModel):
    toml: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "符合 PEP 621 的 pyproject.toml 配置内容"
        }
    )

class LLMGeneratedReadmeRequire(BaseModel):
    readme: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "符合 GitHub 标准的 README 内容，包含安装和使用指南"
        }
    )

@run_agent
def run(agent: MofaAgent):
    env_file_path = os.path.join(agent_config_dir_path, '.env.secret')
    agent_config_path = os.path.join(agent_config_dir_path, 'configs', 'agent.yml')
    
    # 接收所有必需参数
    receive_data = agent.receive_parameters(['query', 'agent_config', 'agent_code'])
    agent_name = json.loads(receive_data.get('agent_config')).get('agent_name')
    module_name = json.loads(receive_data.get('agent_config')).get('module_name')
    agent_code = json.loads(receive_data.get('agent_code')).get('llm_generated_code', '')
    
    # 生成 pyproject.toml
    result = generate_agent_config(
        response_model=LLMGeneratedTomlRequire,
        user_query=receive_data.get('query'),
        agent_config_path=agent_config_path,
        env_file_path=env_file_path,
        add_prompt=f"agent_name: {agent_name} module_name: {module_name}",
        prompt_selection='pyproject_prompt'
    )
    
    # 生成 README.md
    readme_result = generate_agent_config(
        response_model=LLMGeneratedReadmeRequire,
        user_query=str(agent_code),
        agent_config_path=agent_config_path,
        env_file_path=env_file_path,
        prompt_selection='readme_prompt',
        add_prompt=f"agent_name: {agent_name} module_name: {module_name}"
    )
    
    # 如果提供了 agent_name 则写入文件
    if agent_name:
        make_dir(f"{agent_name}/{module_name}")
        write_file(data=readme_result.readme, file_path=f"{agent_name}/README.md")
        write_file(data=result.toml, file_path=f"{agent_name}/pyproject.toml")
    
    agent.send_output(agent_output_name='dependency_generator_result', agent_result=result.json())
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **toml**：用于 TOML 文件解析和生成
- **pydantic**：用于结构化数据模型（由 mofa 框架使用）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

## 生成的 PyProject.toml 特性

### 自动依赖检测
- **HTTP 库**：`requests.get()` → 添加 `requests = "*"`
- **数据处理**：`pandas.DataFrame()` → 添加 `pandas = "*"`
- **机器学习**：`import torch` → 添加 `torch = "*"`
- **Web 框架**：`from fastapi import` → 添加 `fastapi = "*"`

### 模板结构
```toml
[tool.poetry]
name = "{agent_name}"
version = "0.1.0"
description = "自动生成的代理包"
authors = ["Mofa Bot <mofa-bot@moxin.com>"]
packages = [{ include = "{module_name}" }]

[tool.poetry.dependencies]
python = ">=3.10"
pyarrow = ">= 5.0.0"
# 基于代码模式自动检测的依赖

[tool.poetry.scripts]
{agent_name} = "{module_name}.main:main"
```

## 生成的 README 特性

### 标准部分
- 项目描述和标语
- 功能列表，带有要点
- 安装说明
- 基本使用，包含 YAML 配置示例
- 与其他节点连接的集成示例
- API 参考表格，用于输入/输出主题
- 许可信息

### 高级功能
- **Mermaid 图表**：复杂节点的自动工作流可视化
- **集成示例**：用于与其他节点连接的 YAML 配置
- **API 文档**：输入/输出规范的结构化表格
- **元数据示例**：正确数据格式的 JSON 示例

## 使用场景

- **自动化包创建**：从代理代码生成完整的 Python 包
- **依赖管理**：自动检测并包含所需依赖项
- **文档生成**：为代理存储库创建综合 README 文件
- **CI/CD 集成**：生成适合自动化构建和部署的文件
- **开源合规**：确保生成的包中有适当的许可和归属

## 贡献

1. 确保您的代码遵循现有风格
2. 使用各种代码模式测试依赖检测
3. 使用 `tomlkit.parse()` 验证生成的 TOML 文件
4. 根据需要更新文档模板

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://github.com/moxin-org/mofa)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Poetry 文档](https://python-poetry.org/docs/)