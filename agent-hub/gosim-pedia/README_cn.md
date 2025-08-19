# GoSim-Pedia 节点

一个复杂的 MOFA 节点，通过聚合多个来源的信息来创建全面的演讲者传记。该节点专门使用 AI 驱动的分析和多源数据集成为演讲者、专业人士和公众人物生成详细、结构良好的传记。

## 功能特性

- **多源数据聚合**：结合网络搜索、网络爬虫、RAG 系统和社交媒体的信息
- **AI 驱动分析**：使用高级 LLM 功能提取和构建演讲者信息
- **综合传记生成**：创建具有时间顺序职业路径的详细演讲者档案
- **社交媒体集成**：自动搜索并包含社交媒体存在
- **结构化输出**：生成具有丰富元数据的 markdown 格式传记
- **多媒体内容**：包括图像、视频、博客和出版物链接

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
LLM_BASE_URL=https://api.openai.com/v1  # 可选，用于自定义端点
LLM_MODEL_NAME=gpt-4o  # 可选，默认为 gpt-4o

# 替代 OpenAI 配置
OPENAI_API_KEY=your_openai_api_key_here  # LLM_API_KEY 的替代方案
```

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `query` | string | 是 | 要研究的演讲者姓名或简要描述 |
| `firecrawl_result` | JSON | 是 | 来自 Firecrawl 代理的网络爬虫结果 |
| `serper_result` | JSON | 是 | 来自 Serper 搜索代理的搜索结果 |
| `rag_result` | JSON | 是 | 来自 GoSim-RAG 代理的 RAG 系统结果 |
| `firecrawl_link_result` | JSON | 是 | 社交媒体和链接爬虫结果 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `speaker_query` | string | 处理过的演讲者姓名和组织，用于目标搜索 |
| `speaker_link_query` | string | 用于查找演讲者社交媒体和在线存在的专门查询 |
| `speaker_summary` | string | 全面的 markdown 格式演讲者传记 |

## 使用示例

### 基本数据流配置

```yaml
# gosim-pedia-dataflow.yml
nodes:
  - id: dora-openai-server
    build: pip install -e ../../node-hub/dora-openai-server
    path: dora-openai-server
    outputs:
      - v1/chat/completions
    inputs:
       v1/chat/completions: gosim-pedia-agent/speaker_summary

  - id: gosim-pedia-agent
    build: pip install -e ../../agent-hub/gosim-pedia
    path: gosim-pedia
    outputs:
      - speaker_query
      - speaker_link_query
      - speaker_summary
    inputs:
      query: dora-openai-server/v1/chat/completions
      firecrawl_result: firecrawl-agent/firecrawl_agent_result
      serper_result: serper-search-agent/serper_result
      rag_result: gosim-rag-agent/gosim_rag_result
      firecrawl_link_result: firecrawl-link-agent/firecrawl_agent_result
    env:
      WRITE_LOG: true

  - id: firecrawl-agent
    build: pip install -e ../../agent-hub/firecrawl-agent
    path: firecrawl-agent
    outputs:
      - firecrawl_agent_result
    inputs:
      query: gosim-pedia-agent/speaker_query
    env:
      WRITE_LOG: true

  - id: serper-search-agent
    build: pip install -e ../../agent-hub/serper-search
    path: serper-search
    outputs:
      - serper_result
    inputs:
      query: gosim-pedia-agent/speaker_query
    env:
      WRITE_LOG: true

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

### 运行节点

1. **设置环境变量：**
   ```bash
   echo "LLM_API_KEY=your_openai_api_key" > .env.secret
   echo "LLM_MODEL_NAME=gpt-4o" >> .env.secret
   ```

2. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

3. **构建并启动数据流：**
   ```bash
   dora build gosim-pedia-dataflow.yml
   dora start gosim-pedia-dataflow.yml
   ```

4. **发送演讲者研究查询：**
   示例：
   - "Dr. Jane Smith, MIT 的 AI 研究员"
   - "John Doe, TechCorp 的 CEO"
   - "Prof. Maria Garcia, 量子计算专家"

## 代码示例

核心功能在 `main.py` 中实现：

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from openai import OpenAI
import json
from dotenv import load_dotenv

@run_agent
def run(agent: MofaAgent):
    env_file = '.env.secret'
    load_dotenv(env_file)
    query = agent.receive_parameter('query')
    
    # 创建 OpenAI 客户端
    llm_client = create_openai_client()
    
    # 提取演讲者信息
    speaker_info = get_llm_response(
        client=llm_client, 
        messages=[
            {"role": "system", "content": extract_speaker_prompt},
            {"role": "user", "content": query},
        ]
    )
    
    # 处理演讲者信息
    speaker_info_data = json.loads(speaker_info.replace('\n', '').replace('```json', '').replace('\n```', '').replace('```', ''))
    speaker_name_and_organization = speaker_info_data.get('name') + ' - ' + speaker_info_data.get('organization')
    
    # 发送目标搜索查询
    agent.send_output(agent_output_name='speaker_query', agent_result=speaker_name_and_organization)
    
    # 生成专门的社交媒体搜索查询
    speaker_link_search = f'"{speaker_info_data.get("name")}" ({speaker_info_data.get("organization")}) (site:github.com OR site:linkedin.com OR site:twitter.com OR site:x.com)'
    agent.send_output(agent_output_name='speaker_link_query', agent_result=speaker_link_search)
    
    # 接收来自其他代理的结果
    tool_results = agent.receive_parameters([
        'firecrawl_result', 'serper_result', 'rag_result', 'firecrawl_link_result'
    ])
    
    # 生成综合传记
    summary_messages = [
        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": 'firecrawl_result: ' + json.dumps(tool_results.get('firecrawl_result'))},
        {"role": "user", "content": 'serper_result: ' + json.dumps(tool_results.get('serper_result'))},
        {"role": "user", "content": 'rag_result : ' + json.dumps(tool_results.get('rag_result'))},
        {"role": "user", "content": 'firecrawl_link_result : ' + json.dumps(tool_results.get('firecrawl_link_result'))},
    ]
    
    summary_speaker_info = get_llm_response(client=llm_client, messages=summary_messages)
    agent.send_output('speaker_summary', summary_speaker_info)
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **openai**：用于 OpenAI API 集成（需要添加到 pyproject.toml）
- **python-dotenv**：用于环境变量管理（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

**注意**：该节点需要 `openai` 和 `python-dotenv`，应该添加到 `pyproject.toml` 中。

## 核心特性

### 信息提取
- **演讲者档案分析**：从输入中提取姓名、组织、关键词和职业历程
- **多源集成**：结合来自网络爬虫、搜索引擎和 RAG 系统的数据
- **社交媒体发现**：自动生成社交媒体存在的目标查询
- **结构化处理**：将非结构化数据转换为有组织的传记信息

### 传记生成
- **综合章节**：包括个人信息、职业路径、出版物、奖项等
- **时间顺序组织**：以时间线格式呈现信息以确保清晰度
- **丰富媒体集成**：整合图像、视频、博客和出版物链接
- **专业格式化**：生成具有适当分段和引用的干净 markdown

### 多代理协调
- **查询分发**：向不同的研究代理发送专门查询
- **结果聚合**：收集和综合来自多个来源的结果
- **智能编排**：协调 firecrawl、serper 和 RAG 代理
- **输出优化**：结合所有数据源以实现全面的传记覆盖

## 传记章节

生成的传记包括以下综合章节：

### 核心信息
- **个人信息**：全名、当前职位、教育背景、位置
- **职业路径**：专业职位和成就的时间顺序
- **角色描述**：当前职位和主要职责的概述

### 专业细节  
- **主要贡献**：在其领域的重大成就和创新
- **出版物**：带有描述和链接的著名出版物列表
- **奖项和认可**：整个职业生涯中获得的荣誉和奖项
- **媒体露面**：采访、播客和媒体报道

### 个人洞察
- **传记**：专业背景和职业历程
- **个人洞察**：关于其专业历程的轶事和反思
- **影响和冲击**：对其在领域或行业中影响的描述

### 数字存在
- **社交媒体存在**：Twitter、LinkedIn、GitHub、个人网站的链接
- **公共活动**：会议演讲、网络研讨会和演讲活动
- **多媒体内容**：图像、视频和博客文章以及适当的引用

## 使用场景

### 活动管理
- **演讲者档案**：为会议演讲者生成综合档案
- **小组准备**：为小组讨论者创建详细背景
- **介绍材料**：为演讲者介绍提供丰富内容
- **营销内容**：生成突出演讲者专业知识的推广内容

### 学术研究
- **研究者档案**：为合作编制详细的学术传记
- **引用分析**：跟踪出版物和研究贡献
- **网络映射**：理解学术联系和合作
- **影响评估**：评估研究者影响和贡献

### 商业智能
- **高管档案分析**：研究商业领袖和决策者
- **合作伙伴评估**：评估潜在合作者和伙伴
- **行业分析**：了解特定领域的关键参与者
- **尽职调查**：商业决策的综合背景研究

### 媒体和新闻
- **采访准备**：为采访收集综合背景
- **档案文章**：为特稿故事生成详细档案
- **专家寻源**：识别和研究主题专家
- **事实验证**：跨多个来源交叉参考信息

## 高级配置

### 自定义提示
该节点使用复杂的提示进行信息提取和传记生成：

- **提取演讲者提示**：关键演讲者信息的结构化提取
- **摘要提示**：包含 22 个详细章节的综合传记编写
- **专业语调**：维持第三人称视角以确保专业传记

### 集成要求
该节点需要与多个其他 MOFA 代理集成：

- **Firecrawl 代理**：用于网络爬虫和内容提取
- **Serper 搜索代理**：用于网络搜索结果和信息收集
- **GoSim-RAG 代理**：用于基于 RAG 的信息检索
- **OpenAI 服务器**：用于 LLM 处理和响应生成

## 故障排除

### 常见问题
1. **API 密钥错误**：确保 OpenAI API 密钥有效且有足够的配额
2. **缺少依赖项**：验证所有必需的代理都已正确配置
3. **数据质量**：确保输入源提供足够的传记信息
4. **内存使用**：大型传记数据集可能消耗大量内存

### 调试技巧
- 使用 `WRITE_LOG: true` 环境变量启用详细日志记录
- 检查 API 密钥有效性和配额限制
- 验证所有依赖代理正在运行并响应
- 监控互连代理之间的数据流

## 性能优化

### 处理效率
- **并行处理**：多个代理并发工作以收集信息
- **目标查询**：专门查询优化信息检索
- **数据过滤**：智能过滤减少处理开销
- **缓存利用**：在可能的地方重用结果以提高性能

### 质量保证
- **多源验证**：跨多个来源交叉参考信息
- **结构化验证**：验证数据结构和完整性
- **内容质量**：确保传记准确性和专业呈现
- **链接验证**：验证 URL 和多媒体引用

## 贡献

1. 使用各种演讲者类型和领域进行测试
2. 增强特定行业的传记模板
3. 改进社交媒体发现算法
4. 添加对其他数据源和格式的支持

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://mofa.ai/)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [OpenAI API](https://platform.openai.com/docs/api-reference)