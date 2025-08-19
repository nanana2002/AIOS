# Memory Reasoner 节点

一个提供智能推理功能并集成内存上下文的 MOFA 节点。该节点专门使用检索到的内存数据处理任务，通过 DSPy 驱动的推理代理将历史上下文与当前查询相结合来生成明智的响应。

## 功能特性

- **内存增强推理**：将内存上下文集成到推理过程中
- **DSPy 集成**：利用 DSPy 框架进行结构化推理和提示优化
- **上下文处理**：使用相关历史信息处理任务
- **可配置 LLM 支持**：通过环境配置兼容各种语言模型
- **灵活的代理配置**：基于 YAML 的推理行为配置
- **动态任务处理**：具有内存上下文的实时任务处理

## 安装

以开发模式安装包：

```bash
pip install -e .
```

## 配置

### 环境配置 (`.env.secret`)
必需的环境变量：

```bash
# LLM 配置
LLM_API_KEY=your_api_key_here
LLM_MODEL_NAME=gpt-4o-mini  # 可选，默认：gpt-4o-mini
LLM_API_URL=your_custom_api_url  # 可选，用于自定义端点

# 处理配置
TASK=default_task_description  # 可选的默认任务
IS_DATAFLOW_END=false         # 数据流结束标志
```

### 代理配置 (`configs/config.yml`)
配置推理代理行为：

```yaml
system:
  env:
    proxy_url: null
    agent_type: reasoner

agent:
  prompt:
    role: Knowledgeable Assistant
    backstory: |
      您是一个由 AI 驱动的助手，可以访问跨多个领域的庞大知识数据库，
      包括历史、科学、文学和地理。您的目的是为用户提出的任何问题
      提供准确、简洁和相关的答案。
    task: null
```

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `task` | string | 是 | 要处理的推理任务或查询 |
| `memory_context` | string | 是 | 检索到的用于推理的内存数据 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `reasoner_result` | string | 结合任务和内存上下文的推理结果 |

## 使用示例

### 与内存系统集成

该节点通常用作内存增强推理管道的一部分：

```yaml
# mem0_dataflow.yml（摘录）
- id: memory-agent
  build: pip install -e ../../agent-hub/memeory-agent
  path: memeory-agent
  outputs:
    - memory_retrieval_result
    - memory_record_result
  inputs:
    query: terminal-input/data
    agent_result: reasoner/reasoner_result

- id: reasoner
  build: pip install -e ../../agent-hub/memory-reasoner
  path: memory-reasoner
  inputs:
    task: terminal-input/data
    memory_context: memory-agent/memory_retrieval_result
  outputs:
    - reasoner_result
```

### 独立配置

```yaml
# reasoner-dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      reasoner_result: memory-reasoner/reasoner_result

  - id: memory-reasoner
    build: pip install -e ../../agent-hub/memory-reasoner
    path: memory-reasoner
    outputs:
      - reasoner_result
    inputs:
      task: terminal-input/data
      memory_context: terminal-input/data  # 或来自内存系统
    env:
      IS_DATAFLOW_END: true
```

### 运行节点

1. **设置环境变量：**
   ```bash
   echo "LLM_API_KEY=your_api_key" > .env.secret
   echo "LLM_MODEL_NAME=gpt-4o-mini" >> .env.secret
   ```

2. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

3. **构建并启动数据流：**
   ```bash
   dora build mem0_dataflow.yml
   dora start mem0_dataflow.yml
   ```

4. **推理器将：**
   - 接收任务和内存上下文
   - 使用 DSPy 推理处理信息
   - 生成上下文感知的响应
   - 输出推理结果供进一步处理

## 代码示例

核心功能在 `main.py` 中实现：

```python
import json
import os
from mofa.agent_build.base.base_agent import BaseMofaAgent
from mofa.run.run_agent import run_dspy_agent
from mofa.utils.files.read import flatten_dict_simple, read_yaml

class ReasonerAgent(BaseMofaAgent):
    
    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        if config_path is None:
            config_path = self.config_path
        
        self.init_llm_config()
        config = flatten_dict_simple(nested_dict=read_yaml(file_path=config_path))
        
        # 从环境加载 LLM 配置
        config['model_api_key'] = os.environ.get('LLM_API_KEY')
        config['model_name'] = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')
        
        if os.environ.get('LLM_API_URL', None) is not None:
            config['model_api_url'] = os.environ.get('LLM_API_URL')
        
        return config

    def run(self, memory_context: str, task: str = None, *args, **kwargs):
        config = self.load_config()
        config['task'] = task
        
        # 如果可用，集成内存上下文
        if len(memory_context) > 0:
            config['input_fields'] = {"memory_data": memory_context}
            print(config['input_fields'])
        
        # 运行 DSPy 驱动的推理代理
        agent_result = run_dspy_agent(agent_config=config)
        return agent_result

# 带动态节点处理的主执行
def main():
    parser = argparse.ArgumentParser(description="Reasoner Agent")
    parser.add_argument("--name", type=str, default="arrow-assert")
    parser.add_argument("--task", type=str, default="Paris Olympics")
    parser.add_argument("--memory_context", type=str, default="")
    
    args = parser.parse_args()
    node = Node(args.name)
    
    task = None
    memory_context = None
    load_dotenv('.env.secret')
    
    for event in node:
        if event["type"] == "INPUT" and event['id'] in ['task', 'data']:
            task = event["value"][0].as_py()
            print('任务:', task)
        
        if event["type"] == "INPUT" and event['id'] in ["memory_context"]:
            memory_context = load_node_result(event["value"][0].as_py())
            print('内存上下文:', memory_context)
        
        if task is not None and memory_context is not None:
            reasoner = ReasonerAgent(
                config_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), ) + '/configs/config.yml',
                llm_config_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), ) + '/.env.secret'
            )
            
            result = reasoner.run(task=task, memory_context=memory_context)
            print('推理结果:', result)
            
            output_name = 'reasoner_result'
            node.send_output(
                output_name, 
                pa.array([create_agent_output(
                    agent_name=output_name, 
                    agent_result=result, 
                    dataflow_status=os.getenv('IS_DATAFLOW_END', False)
                )]), 
                event['metadata']
            )
            
            task, memory_context = None, None
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **flask**：用于网络服务器功能
- **mem0ai** (>= 0.1.97)：用于内存集成兼容性
- **dspy**：用于结构化推理和提示优化（需要添加到 pyproject.toml）
- **python-dotenv**：用于环境变量管理（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

**注意**：该节点需要 `dspy` 和 `python-dotenv`，应该添加到 `pyproject.toml` 中。

## 核心特性

### DSPy 驱动的推理
- **结构化提示**：使用 DSPy 框架进行优化的提示工程
- **推理优化**：推理模式的自动优化
- **模块化组件**：用于复杂任务的可组合推理模块
- **性能跟踪**：内置指标和性能监控

### 内存集成
- **上下文感知**：将检索到的记忆整合到推理过程中
- **上下文理解**：使用历史信息来指导当前决策
- **内存导向响应**：基于过去交互和知识生成响应
- **动态上下文**：根据可用的内存数据调整推理

### 配置灵活性
- **环境驱动**：通过环境变量进行配置
- **自定义端点**：支持自定义 LLM API 端点
- **模型选择**：轻松在不同语言模型之间切换
- **代理自定义**：基于 YAML 的代理个性和行为配置

## 推理过程

### 输入处理
1. **任务接收**：从输入接收推理任务
2. **内存上下文**：检索相关内存上下文
3. **上下文集成**：将任务与内存数据结合
4. **配置加载**：加载推理代理配置

### DSPy 推理执行
1. **代理初始化**：使用配置设置 DSPy 推理代理
2. **上下文准备**：准备内存数据作为输入字段
3. **推理执行**：运行结构化推理过程
4. **结果生成**：基于任务和内存产生推理输出

### 输出传递
1. **结果处理**：格式化推理结果
2. **输出传输**：将结果发送到下游组件
3. **状态管理**：处理数据流状态和完成信号

## 使用场景

### 知识增强问答系统
- **历史上下文**：使用过去的对话历史回答问题
- **领域专业知识**：使用累积的知识提供特定领域的答案
- **个性化响应**：根据用户历史和偏好生成个性化响应
- **学习系统**：通过内存集成随着时间改进响应

### 决策支持系统
- **历史分析**：基于过去的结果和经验做出决策
- **模式识别**：从内存中识别模式以指导当前决策
- **风险评估**：使用历史数据和上下文评估风险
- **战略规划**：基于过去的成功和失败制定策略

### 教育应用
- **自适应学习**：根据学生历史调整教学方法
- **进度跟踪**：监控学习进度并相应调整内容
- **个性化辅导**：提供个性化的教育体验
- **知识评估**：基于交互历史评估理解程度

## 高级配置

### 自定义推理代理
```yaml
agent:
  prompt:
    role: Domain Expert
    backstory: |
      您是 [特定领域] 的专业专家，拥有多年分析复杂问题的经验，
      基于历史数据和当前上下文提供战略洞察。
    task: |
      使用当前信息和历史上下文分析给定任务，
      提供全面、可操作的洞察。
```

### 多模型配置
```bash
# 根据任务复杂性支持不同模型
LLM_MODEL_NAME=gpt-4o          # 用于复杂推理
LLM_FALLBACK_MODEL=gpt-4o-mini # 用于简单任务
LLM_API_URL=custom_endpoint    # 自定义 API 端点
```

### 内存上下文优化
```python
def optimize_memory_context(memory_data, task):
    # 基于任务相关性过滤和排名内存
    relevant_memories = filter_memories(memory_data, task)
    ranked_memories = rank_by_relevance(relevant_memories, task)
    return format_for_reasoning(ranked_memories)
```

## 集成模式

### 内存-推理-行动循环
```
内存搜索 → 上下文检索 → 推理 → 行动 → 内存更新
    ↓         ↓         ↓     ↓       ↓
  查询     历史      明智   行动     更新
  处理     上下文    决策   执行     知识
```

### 多代理协作
```yaml
# 与专门代理的协作推理
Scientific Reasoner → Memory Context → Business Reasoner → Decision Synthesis
```

## 性能优化

### 推理效率
- **上下文过滤**：将内存上下文过滤到最相关的信息
- **提示优化**：使用 DSPy 优化提升推理性能
- **模型选择**：根据任务复杂性选择合适的模型
- **缓存**：为相似任务和上下文缓存推理结果

### 内存集成优化
- **上下文摘要**：为效率摘要大的内存上下文
- **相关性评分**：按相关性对内存项目评分和排名
- **上下文限制**：设置内存上下文大小限制以获得最佳性能
- **并行处理**：并行处理内存和推理任务

## 故障排除

### 常见问题
1. **DSPy 导入错误**：确保 DSPy 正确安装和配置
2. **内存上下文格式**：验证内存上下文格式正确
3. **配置加载**：检查 YAML 配置文件语法
4. **API 连接**：验证 LLM API 连接和凭据

### 调试技巧
- 监控任务和内存上下文输入
- 为 DSPy 推理过程启用详细日志记录
- 首先使用简化的任务和内存上下文进行测试
- 验证配置加载和环境变量设置
- 检查 LLM API 响应时间和配额

## 安全考虑

### 内存隐私
- **上下文清理**：清理内存上下文中的敏感信息
- **访问控制**：为内存数据实施适当的访问控制
- **数据加密**：考虑加密敏感的内存上下文
- **审计日志**：记录推理操作以进行安全审计

## 贡献

1. 使用各种推理场景和内存上下文进行测试
2. 优化 DSPy 集成以获得更好的推理性能
3. 添加对其他推理框架的支持
4. 增强内存上下文处理和优化

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://mofa.ai/)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [DSPy 框架](https://github.com/stanfordnlp/dspy)
- [Mem0 AI](https://github.com/mem0ai/mem0)