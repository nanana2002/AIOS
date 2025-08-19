# Firecrawl Agent 节点

一个提供高级网络爬虫和深度研究功能的 MOFA 节点，使用 Firecrawl API。该节点专门进行全面的网站分析，通过 AI 驱动的分析和洞察从网站中提取结构化信息。

## 功能特性

- **高级网络爬虫**：利用 Firecrawl API 进行全面的网站分析
- **深度研究模式**：执行多深度爬虫，智能内容提取
- **AI 驱动分析**：包含结构化数据提取的内置分析提示
- **可配置参数**：可自定义爬虫深度、URL 限制和时间约束
- **活动监控**：提供爬虫进度和活动的实时反馈
- **结构化输出**：以 JSON 格式返回源数据和最终分析

## 安装

以开发模式安装包：

```bash
pip install -e .
```

## 配置

### 环境配置 (`.env.secret`)
必需的环境变量：

```bash
# Firecrawl API 配置
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# 可选配置
FIRECRAWL_MAXDEPTH=3           # 最大爬虫深度（默认：3）
FIRECRAWL_MAXURLS=15          # 要分析的最大 URL 数（默认：15）
ANALYSIS_PROMPT=custom_prompt  # 自定义分析提示（可选）
```

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `query` | string | 是 | 深度研究的搜索查询或主题 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `firecrawl_agent_result` | string (JSON) | 来自网络爬虫的组合源数据和分析结果 |

## 使用示例

### 基本数据流配置

```yaml
# firecrawl_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      firecrawl_agent_result: firecrawl-agent/firecrawl_agent_result

  - id: firecrawl-agent
    build: pip install -e ../../agent-hub/firecrawl-agent
    path: firecrawl-agent
    outputs:
      - firecrawl_agent_result
    inputs:
      query: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### 运行节点

1. **设置环境变量：**
   ```bash
   echo "FIRECRAWL_API_KEY=your_firecrawl_api_key" > .env.secret
   echo "FIRECRAWL_MAXDEPTH=3" >> .env.secret
   echo "FIRECRAWL_MAXURLS=15" >> .env.secret
   ```

2. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

3. **构建并启动数据流：**
   ```bash
   dora build firecrawl_dataflow.yml
   dora start firecrawl_dataflow.yml
   ```

4. **发送研究查询：**
   示例：
   - "研究马斯克的信息"
   - "分析量子计算的最新发展"
   - "查找 OpenAI 领导层的详细信息"

## 代码示例

核心功能在 `main.py` 中实现：

```python
from firecrawl.firecrawl import FirecrawlApp
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
import json
import os
from dotenv import load_dotenv

class FireCrawl:
    def __init__(self, api_key: str = None, env_file: str = '.env.secret', crawl_params: dict = None):
        if api_key is None:
            load_dotenv(env_file)
            api_key = os.getenv("FIRECRAWL_API_KEY")
        
        self.crawl = FirecrawlApp(api_key=api_key)
        
        if crawl_params is None:
            crawl_params = {
                "maxDepth": os.getenv('FIRECRAWL_MAXDEPTH', 3),
                "timeLimit": 180,  # 时间限制（秒）
                "maxUrls": os.getenv('FIRECRAWL_MAXURLS', 15)
            }
        self.crawl_params = crawl_params

    def deep_research(self, query: str, analysis_prompt: str = None):
        if analysis_prompt is None:
            analysis_prompt = """
            发展历程：在行业中的成长路径、主要成就和技术突破。
            个人故事：背景、职业转型和面临的挑战以及如何克服。
            教育背景：教育历史，包括学位和就读大学。
            专利：是否持有技术专利。
            专业经验：工作历史，包括公司和关键项目。
            """
        
        results = self.crawl.deep_research(
            query=query,
            max_depth=os.getenv('FIRECRAWL_MAXDEPTH', 3),
            max_urls=os.getenv('FIRECRAWL_MAXURLS', 10),
            on_activity=self.on_activity,
            analysis_prompt=analysis_prompt
        )
        
        source_data = results['data']['sources']
        analysis_data = results['data']['finalAnalysis']
        return source_data, analysis_data

@run_agent
def run(agent: MofaAgent):
    load_dotenv('.env.secret')
    query = agent.receive_parameter('query')
    
    app = FireCrawl()
    scrape_result = json.dumps(app.deep_research(query=query))
    
    agent.send_output(
        agent_output_name='firecrawl_agent_result',
        agent_result=scrape_result
    )
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **firecrawl** (>= 2.4.3)：用于网络爬虫和内容提取
- **python-dotenv**：用于环境变量管理（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

**注意**：该节点需要 `python-dotenv`，应该添加到 `pyproject.toml` 中。

## 核心特性

### 深度研究功能
- **多深度爬虫**：递归爬取网站到指定深度
- **智能内容提取**：使用 AI 识别和提取相关内容
- **来源跟踪**：维护所有爬取来源的详细记录
- **活动监控**：提供爬虫进度的实时反馈

### 可配置分析
- **自定义提示**：支持特定研究需求的自定义分析提示
- **默认模板**：包含全面的默认分析模板
- **结构化输出**：返回原始源数据和分析洞察
- **灵活参数**：可调节的爬虫深度、URL 限制和时间约束

### 专业研究重点
- **背景分析**：提取专业背景和职业历史
- **教育信息**：识别教育背景和资历
- **专利研究**：发现专利信息和知识产权
- **社交媒体整合**：分析社交媒体存在和贡献

## 使用场景

### 专业研究
- **高管档案**：对商业领袖和高管的全面研究
- **学术研究**：对研究人员及其贡献的详细分析
- **竞争情报**：对竞争对手及其领导层的深入分析
- **尽职调查**：商业合作和投资的背景研究

### 内容创作
- **传记写作**：为传记内容收集全面信息
- **采访准备**：播客或采访准备的研究
- **文章研究**：新闻文章和特稿的背景信息
- **演讲者档案**：会议演讲者和主持人的详细档案

### 商业智能
- **市场研究**：分析特定行业的关键参与者
- **人才招聘**：高管招聘和招聘决策的研究
- **合作伙伴评估**：潜在商业伙伴的背景研究
- **投资分析**：投资决策的尽职调查研究

## 高级配置

### 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `FIRECRAWL_MAXDEPTH` | 3 | 网络分析的最大爬虫深度 |
| `FIRECRAWL_MAXURLS` | 15 | 要爬取的最大 URL 数量 |
| `ANALYSIS_PROMPT` | 默认模板 | 结构化提取的自定义分析提示 |

### 自定义分析提示

您可以通过设置 `ANALYSIS_PROMPT` 环境变量来自定义分析焦点：

```bash
export ANALYSIS_PROMPT="关注：技术专长、领导经验、创新记录、行业认可"
```

### 爬虫参数

该节点支持各种爬虫参数：

```python
crawl_params = {
    "maxDepth": 3,        # 爬虫深度
    "timeLimit": 180,     # 最大时间（秒）
    "maxUrls": 15        # 要分析的最大 URL 数
}
```

## 输出格式

该节点返回包含两个主要组件的 JSON 字符串：

```json
[
  {
    "sources": [
      {
        "url": "https://example.com",
        "title": "页面标题",
        "content": "提取的内容...",
        "metadata": {...}
      }
    ],
    "finalAnalysis": {
      "summary": "综合分析...",
      "key_findings": [...],
      "structured_data": {...}
    }
  }
]
```

## 故障排除

### 常见问题
1. **API 密钥错误**：确保 Firecrawl API 密钥有效且有足够的积分
2. **速率限制**：注意 API 速率限制并相应调整爬虫参数
3. **超时问题**：为复杂的研究查询增加时间限制
4. **内存使用**：大型爬虫操作可能消耗大量内存

### 调试技巧
- 通过内置活动回调监控爬虫活动
- 检查 API 密钥有效性和配额限制
- 调整 `maxDepth` 和 `maxUrls` 以获得最佳性能
- 检查网络爬虫操作的网络连接

## 性能优化

### 爬虫效率
- **深度管理**：平衡爬虫深度与性能需求
- **URL 限制**：根据研究范围设置适当的最大 URL 限制
- **时间约束**：配置合理的时间限制以防止长时间运行的操作

### 资源管理
- **内存使用**：在大型爬虫操作期间监控内存消耗
- **API 配额**：跟踪 API 使用情况以避免超过速率限制
- **网络带宽**：考虑大规模爬虫的带宽需求

## 贡献

1. 使用各种研究查询和域名进行测试
2. 针对不同用例优化爬虫参数
3. 增强特定行业的分析提示
4. 添加对其他输出格式的支持

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://github.com/moxin-org/mofa)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Firecrawl](https://github.com/mendableai/firecrawl)
- [Firecrawl 文档](https://github.com/mendableai/firecrawl)