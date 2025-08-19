# Deepseek 节点

一个提供基于 Deepseek API 的 AI 驱动文本分析和内容生成的 MOFA 节点。该节点专门从多个来源合成信息，特别是网络搜索结果，以 Markdown 格式提供准确、深入的响应。

## 功能特性

- **Deepseek AI 集成**：利用强大的 deepseek-chat 模型进行高级语言处理
- **多源分析**：处理用户查询和网络搜索数据，提供全面响应
- **Markdown 输出**：生成具有适当结构和源 URL 的格式化响应
- **可配置提示**：使用基于 YAML 的配置进行灵活的提示管理
- **实时处理**：提供无流式延迟的即时响应

## 安装

以开发模式安装包：

```bash
pip install -e .
```

## 配置

### 环境配置 (`.env.secret`)
必需的环境变量：

```bash
# Deepseek API 配置
LLM_API_KEY=your_deepseek_api_key_here
```

### 代理配置 (`configs/agent.yml`)
该节点使用 YAML 配置文件来定义 AI 代理的行为：

```yaml
agent:
  prompt:
    role: You are an advanced AI agent specializing in analyzing and synthesizing information provided by users.
    backstory: |
      Developed to assist users in making sense of pre-collected data, your main function is to integrate and analyze the information provided to you.
    answer: Optimize the output to be in Markdown format. Include the URLs of the sources in the output.
```

### 输入参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `query` | string | 是 | 要分析的用户问题或主题 |
| `serper_result` | JSON | 是 | 来自 Serper API 的网络搜索结果作为上下文 |

### 输出参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `deepseek_result` | string | Markdown 格式的 AI 生成分析和综合，包含源 URL |

## 使用示例

### 基本数据流配置

```yaml
# deepseek_serper_dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      serper_result: serper-agent/serper_result
      deepseek_result: deepseek-agent/deepseek_result

  - id: serper-agent
    build: pip install -e ../../agent-hub/serper-search
    path: serper-search
    outputs:
      - serper_result
    inputs:
      query: terminal-input/data
    env:
      IS_DATAFLOW_END: false

  - id: deepseek-agent
    build: pip install -e ../../agent-hub/deepseek
    path: deepseek
    outputs:
      - deepseek_result
    inputs:
      query: terminal-input/data
      serper_result: serper-agent/serper_result
    env:
      IS_DATAFLOW_END: true
```

### 运行节点

1. **设置环境变量：**
   ```bash
   echo "LLM_API_KEY=your_deepseek_api_key" > .env.secret
   ```

2. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

3. **构建并启动数据流：**
   ```bash
   dora build deepseek_serper_dataflow.yml
   dora start deepseek_serper_dataflow.yml
   ```

4. **通过终端输入发送查询：**
   示例：
   - "分析可再生能源的最新发展"
   - "人工智能的当前趋势是什么？"
   - "总结气候变化对农业的影响"

## 代码示例

核心功能在 `main.py` 中实现：

```python
from mofa.agent_build.base.base_agent import MofaAgent
import os
from dotenv import load_dotenv
from openai import OpenAI
from deepseek import agent_config_dir_path
from mofa.utils.files.read import read_yaml

def main():
    agent = MofaAgent(agent_name='deepseek')
    while True:
        # 加载环境配置
        load_dotenv(agent_config_dir_path + '/.env.secret')
        
        # 初始化 Deepseek 客户端
        client = OpenAI(
            api_key=os.getenv('LLM_API_KEY'), 
            base_url="https://api.deepseek.com"
        )
        
        # 加载代理配置
        config = read_yaml(file_path=agent_config_dir_path + '/configs/agent.yml')
        system_prompt = json.dumps(config.get('agent').get('prompt'))
        
        # 获取输入
        user_query = agent.receive_parameter(parameter_name='query')
        serper_data = agent.receive_parameter(parameter_name='serper_result')
        
        # 生成响应
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"user query: {user_query} serper search data: {json.dumps(serper_data)}"}
            ],
            stream=False
        )
        
        # 发送输出
        agent.send_output(
            agent_output_name='deepseek_result', 
            agent_result=response.choices[0].message.content
        )
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **openai**：用于 Deepseek API 集成（兼容的 OpenAI 客户端）
- **python-dotenv**：用于环境变量管理（需要添加到 pyproject.toml）
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

**注意**：该节点需要 `python-dotenv`，应该添加到 `pyproject.toml` 中。

## 核心特性

### 高级语言处理
- 利用 Deepseek 的尖端语言模型进行复杂的文本分析
- 能够理解来自多个信息源的上下文
- 生成连贯、结构良好的响应

### 信息综合
- 结合用户查询和网络搜索结果进行全面分析
- 从不同数据源识别关键洞察
- 提供具有适当归因的上下文相关答案

### Markdown 格式化
- 自动以干净的 Markdown 格式化响应
- 包含源 URL 以确保透明度和验证
- 构建内容以获得最佳可读性

## 使用场景

### 研究和分析
- **学术研究**：从多个学术来源合成信息
- **市场分析**：分析各种市场报告的趋势和数据
- **技术文档**：创建全面的技术摘要

### 内容创作
- **文章写作**：生成具有适当引用的充分研究的文章
- **报告生成**：从原始数据创建结构化报告
- **摘要创建**：将复杂信息压缩成易于理解的格式

### 决策支持
- **商业智能**：分析市场数据以进行战略决策
- **政策分析**：为政策建议综合信息
- **竞争分析**：从多个来源理解市场格局

## 集成模式

### 与搜索代理
- 通常与 `serper-search` 代理配对进行网络数据收集
- 处理搜索结果以提取可行的洞察
- 在整个分析过程中保持源归属

### 终端输入集成
- 与终端输入无缝协作进行交互式查询
- 支持实时问答工作流
- 启用动态查询处理

## 故障排除

### 常见问题
1. **API 密钥错误**：验证 Deepseek API 密钥有效且有足够的积分
2. **配置问题**：确保 `agent.yml` 文件格式正确
3. **缺少依赖项**：安装所有必需的包，包括 `python-dotenv`
4. **路径问题**：验证 `agent_config_dir_path` 指向正确的配置目录

### 调试技巧
- 检查 API 密钥有效性和配额限制
- 验证配置文件路径和格式
- 监控 API 调用的网络连接
- 检查输入数据结构的正确 JSON 格式

## 性能考虑

### 响应时间
- 非流式响应在单个输出中提供完整分析
- 处理时间取决于查询复杂性和搜索结果量
- 针对质量而非速度进行优化

### 资源使用
- 最少的本地资源消耗（计算由 Deepseek API 处理）
- 内存使用随输入数据大小扩展
- API 通信需要网络带宽

## 贡献

1. 使用各种查询类型和搜索结果格式进行测试
2. 优化提示工程以获得更好的响应质量
3. 添加对其他输出格式的支持
4. 实施缓存机制以提高性能

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://github.com/moxin-org/mofa)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Deepseek API](https://api.deepseek.com/)
- [OpenAI Python Client](https://github.com/openai/openai-python)