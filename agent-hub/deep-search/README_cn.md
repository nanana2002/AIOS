# Deep Search 节点

一个复杂的 MOFA 节点，使用 AI 驱动的多阶段分析执行全面的深度研究。该节点结合了网络搜索功能和高级 LLM 推理，为任何给定主题提供全面、结构良好的研究报告。

## 功能特性

- **多阶段研究过程**：实现 5 个不同的思考阶段（上下文提取、意图分析、来源评估、矛盾检查、综合）
- **Serper 集成**：使用 Serper API 进行全面的网络搜索结果
- **LLM 驱动分析**：利用 OpenAI 模型进行智能内容生成和分析
- **流式输出**：提供实时流式响应，改善用户体验
- **文章处理**：高级文章去重、过滤和相关性排序
- **来源可信度评估**：基于可信度评估和排序来源
- **综合分析**：生成整合所有研究阶段的详细最终报告

## 安装

以开发模式安装包：

```bash
pip install -e .
```

**注意**：该节点需要额外的依赖项，应添加到 `pyproject.toml` 中：
- `numpy` - 用于数值计算
- `playwright` - 用于网络交互（已导入但不在依赖中）

## 配置

### 环境配置 (`.env.secret`)
所需的环境变量：

```bash
# OpenAI API 配置
LLM_API_KEY=your_openai_api_key_here
LLM_BASE_URL=https://api.openai.com/v1  # 可选，用于自定义端点
LLM_MODEL_NAME=gpt-4o  # 可选，默认为 gpt-4o

# Serper API 配置
SERPER_API_KEY=your_serper_api_key_here
```

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `user_query` | string | 是 | 要调查的研究主题或问题 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `deep_search_result` | string (JSON) | 包含思考阶段和最终综合的流式研究结果 |

## 使用示例

### 基本数据流配置

```yaml
# deepsearch-dataflow.yml
nodes:
  - id: dora-openai-server
    build: pip install -e ../../node-hub/openai-server-stream
    path: openai-server-stream
    outputs:
      - v3/chat/completions
    inputs:      
      v3/chat/completions:
        source: deep-search-agent/deep_search_result
        queue_size: 1000

  - id: deep-search-agent
    build: pip install -e ../../agent-hub/deep-search
    path: deep-search
    outputs:
      - deep_search_result
    inputs:
      user_query: dora-openai-server/v3/chat/completions
```

### 运行节点

1. **设置环境变量：**
   ```bash
   echo "LLM_API_KEY=your_openai_key" > .env.secret
   echo "SERPER_API_KEY=your_serper_key" >> .env.secret
   echo "LLM_MODEL_NAME=gpt-4o" >> .env.secret
   ```

2. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

3. **构建并启动数据流：**
   ```bash
   dora build deepsearch-dataflow.yml
   dora start deepsearch-dataflow.yml
   ```

4. **发送研究查询：**
   示例：
   - "人工智能的最新发展"
   - "气候变化对可再生能源的影响"
   - "医疗保健中的区块链技术应用"

## 代码示例

核心功能在 `main.py` 中实现：

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from mofa.kernel.tools.web_search import search_web_with_serper
import json
import time

@run_agent
def run(agent: MofaAgent):
    user_query = agent.receive_parameter('user_query')
    
    # 使用 Serper 搜索文章
    raw_articles = search_web_with_serper(
        query=user_query, 
        subscription_key=os.getenv("SERPER_API_KEY")
    )
    
    # 处理和过滤文章
    processor = ArticleProcessor(raw_articles)
    processed_articles = processor.process()
    selected_articles = processed_articles[:20]
    
    # 初始化 LLM 客户端和研究生成器
    llm_client = LLMClient(model_name=os.getenv("LLM_MODEL_NAME", "gpt-4o"))
    generator = ResearchGenerator(articles=selected_articles, llm_client=llm_client)
    
    # 生成流式研究结果
    for chunk in generator.generate_stream(user_query=user_query):
        agent.send_output(
            agent_output_name='deep_search_result',
            agent_result=json.dumps(chunk, indent=2)
        )
        time.sleep(0.005)  # 流式处理的小延迟

def main():
    agent = MofaAgent(agent_name='DeepInquire')
    run(agent=agent)
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **python-dotenv**：用于环境变量管理
- **openai**：用于 OpenAI API 集成
- **numpy**：用于数值计算（需要添加到 pyproject.toml）
- **playwright**：用于网络交互（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

## 研究过程阶段

### 1. 上下文提取 (📝)
- 从文章中分离出最有信息价值的片段
- 专注于前 3 个最相关的文章
- 提取关键的上下文信息

### 2. 意图分析 (🔍)
- 从提取的上下文分析核心用户意图
- 确定研究目标和范围
- 识别特定的关注领域

### 3. 来源评估 (📊)
- 基于可信度对文章进行排序
- 优先考虑可信来源（期刊、报告、权威网站）
- 评估信息可靠性

### 4. 矛盾检查 (⚠️)
- 跨来源交叉引用文章以确保信息一致性
- 识别来源间的冲突信息
- 验证事实准确性

### 5. 综合 (🧠)
- 整合所有阶段的验证信息
- 创建全面的理解
- 生成结构化的见解

## 输出格式

该节点生成以下结构的流式 JSON 输出：

```json
{
  "type": "thinking|content|completion",
  "content": "生成的内容块",
  "articles": [{"title": "...", "url": "...", "snippet": "..."}],
  "metadata": {"stage": "阶段名称"},
  "id": "阶段_id-子步骤_id"
}
```

## 使用场景

### 学术研究
- **文献综述**：学术主题的全面分析
- **趋势分析**：识别研究领域的新兴模式
- **空白识别**：发现研究机会和未探索的领域

### 商业智能
- **市场研究**：深入分析市场趋势和机会
- **竞争分析**：理解竞争对手策略和定位
- **技术评估**：评估新兴技术及其潜力

### 新闻和内容创作
- **调查研究**：复杂主题的彻底调查
- **事实核查**：跨多个来源验证声明
- **背景研究**：为新闻故事提供全面背景

## 高级功能

### 文章处理管道
- **去重**：按 URL 移除重复文章
- **质量过滤**：按片段长度和相关性对文章排序
- **来源优先级**：偏好权威来源

### 流式架构
- **实时输出**：在处理过程中提供即时反馈
- **分块处理**：高效处理大数据集
- **进度跟踪**：清楚指示研究进度

## 故障排除

### 常见问题
1. **API 密钥错误**：确保 OpenAI 和 Serper API 密钥有效
2. **速率限制**：注意两个服务的 API 速率限制
3. **网络问题**：验证网络搜索的稳定互联网连接
4. **内存使用**：大型研究主题可能消耗大量内存

### 调试技巧
- 使用环境变量启用详细日志记录
- 检查 API 密钥有效性和配额
- 在搜索期间监控网络连接
- 调整 MAX_ARTICLES 常量以优化内存

## 贡献

1. 使用各种研究主题和领域进行测试
2. 优化文章选择算法
3. 添加对其他搜索提供商的支持
4. 实现缓存机制以提高性能

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://github.com/moxin-org/mofa)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Serper API](https://serper.dev/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)