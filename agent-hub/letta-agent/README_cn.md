# Letta Agent 节点

一个提供持久内存增强 AI 代理功能的 MOFA 节点，使用 Letta（前身为 MemGPT）。该节点专门在处理任务时维护长期交互记忆，非常适合需要跨会话对话连续性和上下文保持的应用。

## 功能特性

- **持久内存管理**：使用 Letta 的高级内存系统进行长期交互存储
- **档案内存集成**：存储和检索过去对话的上下文信息
- **可配置代理人格**：可自定义的代理个性和人类用户档案
- **动态任务处理**：具有内存增强响应的实时任务处理
- **LLM 集成**：通过 Letta 的配置系统兼容各种 LLM 提供商
- **基于嵌入的检索**：使用嵌入模型进行语义内存搜索

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
LLM_API_KEY=your_openai_api_key_here
LLM_MODEL_NAME=gpt-4o
LLM_EMBEDDER_MODEL_NAME=text-embedding-3-small

# 可选配置
TASK=default_task_description  # 可选的默认任务
IS_DATAFLOW_END=true          # 数据流结束标志
```

### 代理配置 (`configs/config.yml`)
配置代理的内存和人格：

```yaml
system: null
agent:
  user_id: mofa_letta
  memory:
    persona: You are a helpful assistant that remembers past interactions
    human: My name is mofa
  user:
    prompt: Hello! I'm here to assist you with any problem or task you're facing. I utilize my memory of previous interactions and a comprehensive knowledge base to provide tailored and effective solutions.
```

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `task` | string | 是 | 要使用内存上下文处理的任务或查询 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `letta_agent_result` | string | 具有存储上下文的内存增强任务响应 |

## 使用示例

### 基本数据流配置

```yaml
# letta_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      letta_agent_result: letta-agent/letta_agent_result

  - id: letta-agent
    build: pip install -e ../../agent-hub/letta-agent
    path: letta-agent
    outputs:
      - letta_agent_result
    inputs:
      task: terminal-input/data
```

### 运行节点

1. **设置环境变量：**
   ```bash
   echo "LLM_API_KEY=your_openai_api_key" > .env.secret
   echo "LLM_MODEL_NAME=gpt-4o" >> .env.secret
   echo "LLM_EMBEDDER_MODEL_NAME=text-embedding-3-small" >> .env.secret
   ```

2. **配置代理设置：**
   编辑 `configs/config.yml` 来自定义代理的人格和内存设置。

3. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

4. **构建并启动数据流：**
   ```bash
   dora build letta_dataflow.yml
   dora start letta_dataflow.yml
   ```

5. **向代理发送任务：**
   示例：
   - "记住我早上喜欢喝咖啡"
   - "我对早晨饮品的偏好是什么？"
   - "根据我们之前的讨论帮我规划一个项目"

## 代码示例

核心功能在 `main.py` 中实现：

```python
from letta import create_client, LLMConfig, EmbeddingConfig
from letta.schemas.memory import ChatMemory
from mofa.agent_build.base.base_agent import BaseMofaAgent

class LettaAgent(BaseMofaAgent):
    def create_llm_client(self, config: dict = None, *args, **kwargs):
        self.init_llm_config()
        llm_config = self.load_config()
        
        # 设置 OpenAI API 密钥
        os.environ["OPENAI_API_KEY"] = os.environ.get('LLM_API_KEY')
        
        # 创建 Letta 客户端
        self.llm_client = create_client()
        
        # 使用内存配置创建代理
        self.agent_state = self.llm_client.create_agent(
            memory=ChatMemory(
                persona=llm_config.get('agent').get('memory').get('persona'),
                human=llm_config.get('agent').get('memory').get('human')
            ),
            llm_config=LLMConfig.default_config(
                model_name=os.environ.get('LLM_MODEL_NAME')
            ),
            embedding_config=EmbeddingConfig.default_config(
                model_name=os.environ.get('LLM_EMBEDDER_MODEL_NAME')
            )
        )

    def send_message_to_agent(self, prompt: str):
        response = self.llm_client.send_message(
            agent_id=self.agent_state_id,
            role="user",
            message=prompt
        )
        
        for message in response.messages:
            if message.message_type == 'tool_call_message':
                tool_call_args = json.loads(message.tool_call.arguments)
                return tool_call_args.get('message')

    def run(self, task: str = None, *args, **kwargs):
        # 检索现有记忆
        memory_data = self.search_memory
        if len(memory_data) > 0:
            memory_context = 'These are the context memories: ' + '\n'.join(memory_data)
        else:
            memory_context = ''
        
        # 使用内存上下文处理任务
        user_message = f"User task: {task}. Memory data: {memory_context}"
        agent_result = self.send_message_to_agent(prompt=user_message)
        
        # 记录新内存
        self.record_memory(data=f'task: {task} agent result: {agent_result}')
        
        return agent_result
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **letta**：用于具有内存功能的 AI 代理能力
- **attrs**：用于类定义和字段管理（需要添加到 pyproject.toml）
- **python-dotenv**：用于环境变量管理（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

**注意**：该节点需要 `attrs` 和 `python-dotenv`，应该添加到 `pyproject.toml` 中。

## 核心特性

### 内存管理
- **档案内存**：对话历史的长期存储和检索
- **上下文回忆**：通过过去交互的语义搜索
- **内存记录**：任务和响应的自动存储
- **内存搜索**：相关历史上下文的高效检索

### 代理配置
- **自定义人格**：可配置的代理个性和行为
- **用户档案**：可自定义的人类用户特征
- **内存初始化**：可配置的起始内存状态
- **灵活设置**：基于 YAML 的配置管理

### LLM 集成
- **多提供商**：通过 Letta 支持各种 LLM 提供商
- **嵌入模型**：用于内存操作的可配置嵌入模型
- **模型灵活性**：轻松在不同模型配置之间切换
- **API 管理**：安全的 API 密钥处理和配置

## 内存系统

### 档案内存
Letta 的档案内存系统提供：
- **语义存储**：具有语义含义的上下文信息存储
- **高效检索**：快速查找相关的过去信息
- **持久存储**：内存在代理会话间持续存在
- **可扩展架构**：处理大量历史数据

### 内存操作
```python
# 搜索现有记忆
memory_data = agent.search_memory

# 添加新记忆
agent.add_memory("需要记住的重要信息")

# 记录任务和结果
agent.record_memory(f"task: {task} result: {result}")
```

## 使用场景

### 对话式 AI
- **客户支持**：在多次支持交互中维护上下文
- **个人助手**：记住用户偏好和历史
- **教育导师**：跟踪学习进度并调整教学方法
- **治疗机器人**：维护治疗关系的连续性

### 任务管理
- **项目协助**：跨会话记住项目细节和进度
- **研究支持**：维护正在进行的研究主题的上下文
- **写作助手**：记住写作风格和项目要求
- **规划工具**：长期跟踪目标和进度

### 知识管理
- **专家系统**：通过交互历史逐步构建专业知识
- **文档助手**：记住组织知识和程序
- **培训系统**：跟踪学习者进度并相应调整内容
- **咨询服务**：维护客户关系历史和偏好

## 高级配置

### 内存人格自定义
```yaml
agent:
  memory:
    persona: |
      您是一位专业的技术助手，在软件开发方面具有专业知识。
      您记住编码偏好、项目详细信息和技术讨论，
      以提供日益个性化和有效的协助。
    human: |
      我是一名从事分布式系统工作的高级软件工程师。
      我偏好 Python，并且在微服务架构方面有经验。
```

### LLM 模型配置
```bash
# 高性能配置
LLM_MODEL_NAME=gpt-4o
LLM_EMBEDDER_MODEL_NAME=text-embedding-3-large

# 成本优化配置
LLM_MODEL_NAME=gpt-3.5-turbo
LLM_EMBEDDER_MODEL_NAME=text-embedding-3-small
```

## 集成模式

### 与其他 MOFA 代理
- **多代理系统**：在不同专门代理之间共享上下文
- **工作流编排**：在复杂的多步骤过程中维护状态
- **上下文移交**：在不同代理类型之间传输相关内存
- **协作处理**：多个代理在共享长期项目上工作

### 会话管理
- **用户会话**：为不同用户维护独立的内存空间
- **项目上下文**：为不同项目或域隔离记忆
- **时间组织**：按时间段或项目阶段组织记忆
- **访问控制**：管理内存访问权限和隐私

## 故障排除

### 常见问题
1. **内存未持久化**：检查 Letta 客户端配置和存储设置
2. **API 密钥错误**：验证 LLM 和嵌入模型 API 密钥
3. **模型加载问题**：确保模型名称正确指定
4. **内存搜索为空**：检查是否正确记录了记忆

### 调试技巧
- 监控内存存储和检索操作
- 检查 Letta 客户端初始化和代理状态
- 验证环境变量配置
- 独立测试内存操作
- 启用详细日志记录进行调试

## 性能优化

### 内存效率
- **内存修剪**：定期清理无关或过时的记忆
- **选择性存储**：仅存储重要信息以减少内存膨胀
- **压缩**：对大内存块使用摘要技术
- **索引**：通过适当的索引策略优化内存搜索

### 响应性能
- **模型选择**：平衡模型能力与响应速度
- **内存限制**：对内存检索设置适当限制
- **缓存**：缓存频繁访问的记忆
- **批处理**：高效处理多个相关任务

## 贡献

1. 使用各种对话模式和内存场景进行测试
2. 增强内存组织和检索算法
3. 添加对其他 LLM 提供商和模型的支持
4. 改进与其他内存管理系统的集成

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://mofa.ai/)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Letta（前身为 MemGPT）](https://github.com/cpacker/MemGPT)
- [Letta 文档](https://docs.letta.com/)