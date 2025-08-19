# GoSim-RAG 节点

一个提供检索增强生成（RAG）功能的 MOFA 节点，使用向量搜索和嵌入技术。该节点专门使用语义相似性搜索从预构建的向量数据库中检索相关信息，非常适合知识检索和上下文感知信息查找。

## 功能特性

- **向量数据库集成**：使用 ChromaDB 进行高效的向量存储和检索
- **基于嵌入的搜索**：利用先进的嵌入模型进行语义相似性匹配
- **可配置搜索参数**：可自定义的搜索深度和嵌入模型选择
- **高性能检索**：优化的向量搜索，可配置结果限制
- **灵活的嵌入支持**：兼容各种嵌入模型，包括 OpenAI 的 text-embedding-3-large
- **环境驱动配置**：通过环境变量轻松配置

## 安装

以开发模式安装包：

```bash
pip install -e .
```

## 配置

### 环境配置 (`.env.secret`)
必需的环境变量：

```bash
# 嵌入 API 配置
EMBEDDING_API_KEY=your_openai_api_key_here  # 用于嵌入的 OpenAI API 密钥
EMBEDDING_MODEL_NAME=text-embedding-3-large  # 可选，默认：text-embedding-3-large

# 向量数据库配置
VECTOR_CHROME_PATH=chroma_store  # 可选，ChromaDB 存储路径（默认：chroma_store）
VECTOR_SEARCH_NUM=12            # 可选，返回的搜索结果数量（默认：12）
```

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `query` | string | 是 | 在向量数据库中查找相关信息的搜索查询 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `gosim_rag_result` | string | 从向量数据库检索的相关文档/片段 |

## 使用示例

### 与 GoSim-Pedia 集成

该节点通常用作更大数据流的一部分，例如在 GoSim-Pedia 系统中：

```yaml
# gosim-pedia-dataflow.yml（摘录）
- id: gosim-rag-agent
  build: pip install -e ../../agent-hub/gosim-rag
  path: gosim-rag
  outputs:
    - gosim_rag_result
  inputs:
    query: gosim-pedia-agent/speaker_query
  env:
    WRITE_LOG: true
```

### 独立使用

```yaml
# simple-rag-dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      gosim_rag_result: gosim-rag-agent/gosim_rag_result

  - id: gosim-rag-agent
    build: pip install -e ../../agent-hub/gosim-rag
    path: gosim-rag
    outputs:
      - gosim_rag_result
    inputs:
      query: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### 运行节点

1. **设置环境变量：**
   ```bash
   echo "EMBEDDING_API_KEY=your_openai_api_key" > .env.secret
   echo "EMBEDDING_MODEL_NAME=text-embedding-3-large" >> .env.secret
   echo "VECTOR_CHROME_PATH=./chroma_store" >> .env.secret
   echo "VECTOR_SEARCH_NUM=12" >> .env.secret
   ```

2. **确保向量数据库存在：**
   确保您在指定路径下有一个预构建的 ChromaDB 向量存储，其中包含已索引的文档。

3. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

4. **构建并启动数据流：**
   ```bash
   dora build simple-rag-dataflow.yml
   dora start simple-rag-dataflow.yml
   ```

5. **发送搜索查询：**
   示例：
   - "人工智能研究"
   - "机器学习应用"
   - "数据科学方法论"

## 代码示例

核心功能在 `main.py` 中实现：

```python
import os
from dotenv import load_dotenv
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from mofa.kernel.rag.embedding.huggingface import load_embedding_model
from mofa.kernel.rag.vector.util import search_vector
from mofa.utils.database.vector.chromadb import create_chroma_db_conn_with_langchain

@run_agent
def run(agent: MofaAgent):
    env_file = '.env.secret'
    load_dotenv(env_file)
    
    # 配置
    chroma_path = os.getenv('VECTOR_CHROME_PATH', 'chroma_store')
    model_name = os.getenv('EMBEDDING_MODEL_NAME', 'text-embedding-3-large')
    search_num = os.getenv('VECTOR_SEARCH_NUM', 12)
    
    # 设置嵌入 API 密钥
    os.environ["OPENAI_API_KEY"] = os.getenv('EMBEDDING_API_KEY')
    
    # 初始化嵌入模型和向量存储
    embedding = load_embedding_model(model_name=model_name)
    vectorstore = create_chroma_db_conn_with_langchain(
        embedding=embedding, 
        db_path=chroma_path
    )
    
    # 接收查询并执行向量搜索
    query = agent.receive_parameter('query')
    vector_results = search_vector(
        vectorstore=vectorstore, 
        keywords=[query], 
        k=search_num
    )
    
    # 发送结果
    agent.send_output(
        agent_output_name='gosim_rag_result',
        agent_result=vector_results
    )

def main():
    agent = MofaAgent(agent_name='gosim-rag-agent')
    run(agent=agent)
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **chromadb**：用于向量数据库操作（需要添加到 pyproject.toml）
- **langchain**：用于向量存储集成（需要添加到 pyproject.toml）
- **openai**：用于嵌入模型 API 调用（需要添加到 pyproject.toml）
- **python-dotenv**：用于环境变量管理（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

**注意**：该节点需要几个应该添加到 `pyproject.toml` 的依赖项：
- `chromadb`
- `langchain`
- `openai` 
- `python-dotenv`

## 核心特性

### 向量搜索功能
- **语义相似性**：使用基于嵌入的搜索进行语义而非关键词匹配
- **可配置结果**：可调节返回结果数量（默认：12）
- **高性能**：优化的向量操作，快速检索
- **相关性排名**：结果按相似性得分自动排名

### 嵌入模型支持
- **多种模型**：支持各种嵌入模型，包括 OpenAI 的最新模型
- **灵活配置**：轻松在不同嵌入提供商之间切换
- **API 集成**：与嵌入服务 API 无缝集成
- **模型优化**：高效的模型加载和缓存

### 数据库集成
- **ChromaDB 后端**：可靠且高性能的向量数据库
- **持久存储**：向量数据在会话间持久化
- **可扩展架构**：高效处理大型文档集合
- **LangChain 集成**：利用 LangChain 进行向量存储操作

## 使用场景

### 知识库搜索
- **文档检索**：从大型集合中查找相关文档
- **FAQ 系统**：检索常见问题的答案
- **技术文档**：搜索技术手册和指南
- **研究论文**：查找相关的学术论文和出版物

### 上下文信息检索
- **演讲者研究**：检索用于传记生成的背景信息
- **主题探索**：查找主题分析的相关内容
- **内容增强**：使用相关上下文增强响应
- **信息综合**：为综合分析收集支持信息

### AI 驱动应用
- **聊天机器人增强**：为对话 AI 系统提供上下文
- **内容生成**：为内容创建提供相关信息
- **问答系统**：为 QA 系统提供相关知识支持
- **推荐系统**：查找相似或相关的内容

## 配置选项

### 向量数据库设置

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `VECTOR_CHROME_PATH` | `chroma_store` | ChromaDB 存储目录路径 |
| `VECTOR_SEARCH_NUM` | `12` | 返回的搜索结果数量 |

### 嵌入配置

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `EMBEDDING_MODEL_NAME` | `text-embedding-3-large` | 使用的嵌入模型 |
| `EMBEDDING_API_KEY` | 必需 | 嵌入服务的 API 密钥 |

### 高级配置

```bash
# 高精度搜索，更多结果
VECTOR_SEARCH_NUM=20
EMBEDDING_MODEL_NAME=text-embedding-3-large

# 性能优化设置
VECTOR_SEARCH_NUM=5
EMBEDDING_MODEL_NAME=text-embedding-3-small
```

## 向量数据库设置

### 前提条件
使用此节点之前，您需要：

1. **创建向量数据库**：使用您的文档构建 ChromaDB 向量存储
2. **生成嵌入**：通过嵌入模型处理您的文档
3. **存储向量**：以 ChromaDB 格式保存嵌入

### 数据库创建示例
```python
from mofa.kernel.rag.embedding.huggingface import load_embedding_model
from mofa.utils.database.vector.chromadb import create_chroma_db_conn_with_langchain

# 加载嵌入模型
embedding = load_embedding_model(model_name='text-embedding-3-large')

# 创建向量存储
vectorstore = create_chroma_db_conn_with_langchain(
    embedding=embedding, 
    db_path='./chroma_store'
)

# 添加文档（示例）
documents = ["文档1内容...", "文档2内容..."]
vectorstore.add_texts(documents)
```

## 故障排除

### 常见问题
1. **缺少向量数据库**：确保 ChromaDB 存储在指定路径下存在
2. **API 密钥错误**：验证嵌入 API 密钥有效且有足够的配额
3. **模型加载错误**：检查嵌入模型名称和可用性
4. **搜索返回空结果**：验证数据库包含已索引的文档

### 调试技巧
- 检查向量数据库路径存在且包含数据
- 验证嵌入 API 密钥和配额限制
- 独立测试嵌入模型加载
- 监控搜索性能并调整结果数量
- 使用 `WRITE_LOG: true` 启用详细日志记录

## 性能优化

### 搜索性能
- **结果限制**：根据需求与性能平衡调整 `VECTOR_SEARCH_NUM`
- **模型选择**：为您的用例使用适当的嵌入模型
- **数据库优化**：确保 ChromaDB 正确索引
- **缓存**：利用嵌入模型缓存处理重复查询

### 资源管理
- **内存使用**：监控大型向量数据库的内存消耗
- **API 调用**：优化嵌入 API 使用以管理成本
- **存储空间**：监控 ChromaDB 存储需求
- **处理时间**：平衡搜索深度与响应时间要求

## 集成模式

### 与其他 MOFA 代理
该节点通常与以下组件结合使用：
- **GoSim-Pedia**：为演讲者传记生成提供上下文
- **搜索代理**：用本地知识补充网络搜索
- **内容生成**：为 AI 内容创建提供相关信息
- **分析代理**：为分析任务提供背景信息

### 数据流模式
```yaml
# 典型集成模式
搜索查询 -> RAG 检索 -> 上下文增强 -> 最终输出
```

## 贡献

1. 使用各种向量数据库大小和配置进行测试
2. 针对特定用例优化搜索算法
3. 添加对其他嵌入模型和提供商的支持
4. 增强与其他向量数据库后端的集成

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://mofa.ai/)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [ChromaDB](https://www.trychroma.com/)
- [LangChain](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI 嵌入](https://platform.openai.com/docs/guides/embeddings)