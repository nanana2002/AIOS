# Memory Agent 节点

一个提供综合内存管理功能的 MOFA 节点，使用 Mem0 AI，结合内存检索和存储操作。该节点作为内存编排器，可以搜索现有记忆、存储新对话，并为 AI 应用程序管理完整的内存生命周期。

## 功能特性

- **内存搜索和检索**：使用语义搜索查询现有记忆
- **内存存储**：存储新的对话消息和上下文
- **双阶段操作**：在单个工作流中结合检索和存储
- **用户特定内存**：为不同用户维护独立的内存空间
- **可配置内存限制**：控制检索记忆的数量
- **实时内存更新**：在对话流程中动态更新内存

## 安装

以开发模式安装包：

```bash
pip install -e .
```

## 配置

### 环境配置 (`.env.secret`)
必需的环境变量：

```bash
# OpenAI API 配置
LLM_API_KEY=your_openai_api_key_here

# 内存配置（可选）
MEMORY_ID=mofa-memory-user  # 内存操作的默认用户ID
MEMORY_LIMIT=5             # 每次搜索检索的记忆数量
```

### 内存配置 (`configs/config.yml`)
配置内存系统：

```yaml
system: null
agent:
  llm:
    provider: openai
    config:
      model: "gpt-4o"
      max_tokens: 3200

  vector_store:
    provider: chroma
    config:
      collection_name: "mofa-memory"
      path: "db"

  embedder:
    provider: openai
    config:
      model: "text-embedding-3-large"

  user_id: "mofa"
```

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `query` | string | 是 | 搜索相关记忆的查询 |
| `agent_result` | string | 是 | 要存储在内存中的 LLM 响应 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `memory_retrieval_result` | string (JSON) | 基于查询检索的相关记忆 |
| `memory_record_result` | string (JSON) | 内存存储操作的确认 |

## 使用示例

### 基本数据流配置

该节点通常用于内存增强的对话流程：

```yaml
# mem0_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      memory_retrieval_result: memory-agent/memory_retrieval_result
      reasoner_result: reasoner/reasoner_result
      memory_record_result: memory-agent/memory_record_result

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

### 运行节点

1. **设置环境变量：**
   ```bash
   echo "LLM_API_KEY=your_openai_api_key" > .env.secret
   echo "MEMORY_ID=user123" >> .env.secret
   echo "MEMORY_LIMIT=5" >> .env.secret
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

4. **系统将：**
   - 基于用户查询搜索记忆
   - 为推理代理提供内存上下文
   - 将新的对话结果存储回内存

## 代码示例

核心功能在 `main.py` 中实现：

```python
import json
import os
from dotenv import load_dotenv
from mofa.agent_build.base.base_agent import run_agent, MofaAgent
from mem0 import Memory
from mofa.utils.files.read import read_yaml

@run_agent
def run(agent: MofaAgent, memory: Memory, user_id: str = None, messages: list = None):
    
    if user_id is None:
        user_id = os.getenv('MEMORY_ID', 'mofa-memory-user')
    
    # 阶段 1：内存检索
    query = agent.receive_parameter('query')
    relevant_memories = memory.search(
        query=query, 
        user_id=user_id, 
        limit=os.getenv('MEMORY_LIMIT', 5)
    )
    
    print('----相关记忆------:', relevant_memories)
    
    # 格式化记忆输出
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
    agent.send_output(
        'memory_retrieval_result', 
        agent_result=json.dumps(memories_str),
        is_end_status=False
    )
    
    # 阶段 2：等待 LLM 响应并存储
    llm_result = agent.receive_parameter('agent_result')
    
    # 创建对话消息
    messages.append({'role': 'user', 'content': query})
    messages.append({'role': 'assistant', 'content': llm_result})
    
    print('------', messages)
    
    # 在内存中存储新对话
    memory.add(messages, user_id=user_id)
    print('所有结果:', memory.get_all(user_id=user_id))
    
    # 发送存储确认
    agent.send_output(
        'memory_record_result', 
        agent_result=json.dumps('Add Memory Success'),
        is_end_status=True
    )

def main():
    agent = MofaAgent(agent_name='memory-agent')
    load_dotenv('.env.secret')
    
    # 加载内存配置
    config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), ) + '/configs/config.yml'
    config_data = read_yaml(str(config_path))
    
    # 设置 OpenAI API 密钥
    os.environ['OPENAI_API_KEY'] = os.getenv('LLM_API_KEY')
    
    # 初始化内存系统
    memory = Memory.from_config(config_data.get('agent'))
    
    # 运行代理
    run(agent=agent, memory=memory, messages=[])
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **mem0ai** (>= 0.1.97)：用于综合内存管理功能
- **flask**：用于网络服务器功能
- **python-dotenv**：用于环境变量管理（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

**注意**：该节点需要 `python-dotenv`，应该添加到 `pyproject.toml` 中。

## 核心特性

### 双阶段内存操作

#### 阶段 1：内存检索
- 接收用户查询
- 使用语义相似性搜索现有记忆
- 返回格式化的相关记忆
- 为下游代理提供内存上下文

#### 阶段 2：内存存储
- 接收处理过的 LLM 响应
- 创建结构化对话消息
- 在内存中存储完整对话
- 确认成功的存储操作

### 内存搜索功能
- **语义搜索**：使用向量嵌入进行智能内存检索
- **相关性排序**：首先返回最相关的记忆
- **可配置限制**：控制检索的记忆数量
- **用户上下文**：维护用户特定的内存上下文

### 内存存储特性
- **对话线程**：保留完整的对话流程
- **基于角色的消息**：使用用户/助手角色构建消息
- **持久存储**：使用 ChromaDB 进行可靠的数据持久化
- **内存增长**：随着时间持续构建内存

## 架构概述

### 内存工作流
```
用户查询 → 内存搜索 → 上下文检索 → LLM 处理 → 响应存储
   ↓         ↓         ↓         ↓         ↓
  输入     语义      内存      AI 代理   内存更新
 参数     匹配      上下文     处理      和存储
```

### 集成模式
```yaml
终端输入 → Memory Agent (搜索) → 推理器 → Memory Agent (存储) → 输出
              ↓                    ↑            ↓
           内存上下文            内存上下文     更新的内存
```

## 使用场景

### 对话式 AI 系统
- **上下文保持**：在多个会话中维护对话历史
- **个性化响应**：使用过去的交互个性化 AI 响应
- **学习系统**：使 AI 能够从用户偏好和反馈中学习
- **多轮对话**：支持复杂、上下文感知的对话

### 客户支持应用
- **案例历史**：维护完整的客户交互历史
- **上下文转移**：在对话在代理之间转移时保持上下文
- **问题跟踪**：记住以前的问题及其解决方案
- **客户洞察**：随着时间构建全面的客户档案

### 教育和培训系统
- **学习进度**：跟踪学生学习模式和进度
- **自适应内容**：根据过去的学习交互调整内容
- **性能监控**：监控和存储学习结果
- **个性化辅导**：提供个性化的教育体验

## 高级配置

### 内存搜索优化
```bash
# 微调内存检索
MEMORY_LIMIT=10        # 增加检索的记忆
MEMORY_THRESHOLD=0.7   # 检索的相似性阈值
MEMORY_DECAY=0.95      # 基于时间的记忆重要性衰减
```

### 多用户内存管理
```python
def handle_multiple_users():
    users = {
        'user1': 'project_alpha_context',
        'user2': 'customer_support_context', 
        'user3': 'educational_context'
    }
    
    for user_id, context in users.items():
        memories = memory.search(query=query, user_id=user_id, limit=5)
        # 为每个用户上下文处理记忆
```

### 内存性能调优
```yaml
agent:
  vector_store:
    provider: chroma
    config:
      collection_name: "high-performance-memory"
      path: "optimized_db"
      distance_function: "cosine"
      
  embedder:
    provider: openai
    config:
      model: "text-embedding-3-large"
      batch_size: 100
```

## 与其他代理集成

### Memory-Reasoner 管道
该节点与 memory-reasoner 代理密切配合：

1. **内存检索**：为推理器提供相关上下文
2. **推理过程**：推理器使用内存上下文处理查询
3. **内存存储**：存储推理器输出供将来参考

### 多代理内存共享
```python
# 跨多个代理共享内存
class SharedMemoryAgent(MofaAgent):
    def __init__(self, shared_memory_config):
        self.memory = Memory.from_config(shared_memory_config)
        # 多个代理可以访问同一个内存实例
```

## 性能优化

### 内存效率
- **智能检索**：优化搜索查询以检索最相关的记忆
- **内存修剪**：实施过时记忆的定期清理
- **批处理操作**：将内存操作分组以获得更好的性能
- **缓存**：缓存频繁访问的记忆

### 存储优化
- **向量压缩**：使用适当的嵌入维度
- **数据库调优**：优化 ChromaDB 配置
- **内存限制**：实施内存增长限制
- **归档策略**：归档旧记忆以维持性能

## 故障排除

### 常见问题
1. **内存搜索返回空**：检查 user_id 一致性和内存初始化
2. **存储失败**：验证 ChromaDB 路径和写权限
3. **API 错误**：确认 OpenAI API 密钥和配额可用性
4. **配置错误**：验证 YAML 配置文件语法

### 调试技巧
- 监控内存搜索结果和存储确认
- 检查 ChromaDB 数据库文件和存储路径
- 验证跨操作的 user_id 一致性
- 首先用简单查询测试内存操作
- 为内存操作启用详细日志记录

## 数据管理

### 内存生命周期
- **创建**：从对话创建新记忆
- **检索**：基于查询检索现有记忆
- **更新**：用新信息更新记忆
- **归档**：归档或删除旧记忆

### 数据隐私
- **用户隔离**：按 user_id 严格分离记忆
- **数据加密**：考虑对敏感内存数据加密
- **访问控制**：为内存数据实施适当的访问控制
- **保留政策**：定义明确的数据保留政策

## 贡献

1. 使用各种内存场景和用户模式进行测试
2. 优化内存搜索和存储算法
3. 添加对其他内存提供商的支持
4. 增强内存生命周期管理功能

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://mofa.ai/)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Mem0 AI](https://github.com/mem0ai/mem0)
- [Mem0 文档](https://docs.mem0.ai/)