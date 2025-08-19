# Browser Use Connector 节点

一个 MOFA 节点，集成了使用 browser-use 库和 ChatOpenAI 的 AI 驱动浏览器自动化。该节点通过结合大语言模型和自动化浏览器控制来执行复杂的网络任务，实现智能的网络交互。

## 功能特性

- **AI 驱动的浏览器自动化**：使用 browser-use 库实现智能网络交互
- **LLM 集成**：利用 ChatOpenAI 进行自然语言理解和任务规划
- **异步处理**：基于 asyncio 构建，支持高效的非阻塞浏览器操作
- **环境配置**：通过环境变量配置 LLM 设置
- **MOFA 框架集成**：标准 MOFA 代理模式，无缝工作流集成
- **灵活的模型支持**：支持各种 OpenAI 模型和自定义 API 端点

## 安装

以开发模式安装包：

```bash
pip install -e .
```

**注意**：该节点需要额外的依赖项，应添加到 `pyproject.toml` 中：
- `langchain-openai` - 用于 OpenAI LLM 集成
- `python-dotenv` - 用于环境变量管理

## 配置

### 环境配置 (`.env.secret`)
LLM 访问所需的环境变量：

```bash
# OpenAI API 配置
LLM_API_KEY=your_openai_api_key_here
LLM_BASE_URL=https://api.openai.com/v1  # 或自定义端点
LLM_MODEL_NAME=gpt-4o  # 可选，默认为 gpt-4o
```

### 代理配置 (`configs/agent.yml`)
基本代理配置文件（目前较为简单）。

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `question` | string | 是 | 要执行的浏览器任务的自然语言描述 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `agent_result` | string | 浏览器自动化任务的最终结果 |

## 使用示例

### 基本数据流配置

```yaml
# hello_browser_use_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      agent_response: browser_use_connector-agent/agent_result
  - id: browser_use_connector-agent
    build: pip install -e ../../agent-hub/browser-use-connector
    path: browser-use-connector
    outputs:
      - agent_result
    inputs:
      question: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### 运行节点

1. **设置环境变量：**
   ```bash
   echo "LLM_API_KEY=your_api_key" > .env.secret
   echo "LLM_BASE_URL=https://api.openai.com/v1" >> .env.secret
   echo "LLM_MODEL_NAME=gpt-4o" >> .env.secret
   ```

2. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

3. **构建并启动数据流：**
   ```bash
   dora build hello_browser_use_dataflow.yml
   dora start hello_browser_use_dataflow.yml
   ```

4. **发送浏览器任务：**
   输入自然语言描述，如：
   - "导航到 Google 并搜索 Python 教程"
   - "访问 GitHub 并找到最受欢迎的 Python 仓库"
   - "访问新闻网站并总结头条新闻"

## 代码示例

核心功能在 `main.py` 中实现：

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv(dotenv_path='.env.secret', override=True)
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
DEFAULT_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o")

@run_agent
def run(agent: MofaAgent):
    # 接收用户问题
    question = agent.receive_parameter('question')
    
    # 异步运行浏览器自动化
    history = asyncio.run(run_browser_use(question))
    
    # 发送结果
    agent.send_output(
        agent_output_name='agent_result',
        agent_result=history.final_result()
    )

async def run_browser_use(question: str):
    # 创建浏览器自动化代理
    agent = Agent(
        task=question,
        llm=ChatOpenAI(
            model=DEFAULT_MODEL_NAME,
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL
        ),
    )
    # 执行任务
    return await agent.run()

def main():
    agent = MofaAgent(agent_name='browser-use-connector')
    run(agent=agent)
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **browser-use** (0.1.40)：核心浏览器自动化库
- **langchain-openai**：用于 OpenAI LLM 集成（需要添加到 pyproject.toml）
- **python-dotenv**：用于环境变量管理（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

## 浏览器自动化功能

browser-use 库提供：

### 网页导航
- 导航到网站和网络应用程序
- 处理页面加载和动态内容
- 管理浏览器标签和窗口

### 元素交互
- 点击按钮、链接和交互元素
- 填写表单和输入字段
- 处理下拉菜单和选择

### 数据提取
- 从网页中提取文本内容
- 捕获屏幕截图和视觉内容
- 解析表格和列表中的结构化数据

### 高级功能
- 处理 JavaScript 重度应用程序
- 管理 cookie 和会话状态
- 执行多步骤工作流程

## 示例使用场景

### 网络研究
```python
# 任务："搜索 AI 的最新发展并总结前 3 个结果"
# 代理将：
# 1. 导航到搜索引擎
# 2. 输入搜索查询
# 3. 提取相关信息
# 4. 总结发现
```

### 电子商务自动化
```python
# 任务："在电商网站上找到 1000 美元以下最便宜的笔记本电脑"
# 代理将：
# 1. 导航到网站
# 2. 使用搜索和筛选
# 3. 比较价格
# 4. 返回推荐
```

### 内容监控
```python
# 任务："检查新闻网站上特定主题的更新"
# 代理将：
# 1. 访问多个新闻源
# 2. 查找相关文章
# 3. 提取关键信息
# 4. 编制摘要报告
```

## 故障排除

### 常见问题
1. **缺少 API 密钥**：确保在 `.env.secret` 中设置了 `LLM_API_KEY`
2. **浏览器依赖**：browser-use 可能需要额外的浏览器二进制文件
3. **异步执行**：确保在自定义实现中正确使用 async/await
4. **速率限制**：注意配置的 LLM 的 API 速率限制

### 调试技巧
- 在数据流配置中启用 `WRITE_LOG: true`
- 查看 browser-use 文档了解浏览器设置要求
- 验证 API 调用的网络连接

## 贡献

1. 确保您的代码遵循现有的异步模式
2. 将缺失的依赖项添加到 pyproject.toml
3. 使用各种浏览器自动化场景进行测试
4. 更新新功能的文档

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://github.com/moxin-org/mofa)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Browser-use 库](https://github.com/browser-use/browser-use)
- [LangChain OpenAI](https://python.langchain.com/docs/integrations/llms/openai)