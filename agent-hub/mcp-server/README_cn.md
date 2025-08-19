# MCP Server 节点

一个提供 MCP（模型上下文协议）服务器功能的 MOFA 节点，用于将工具和函数作为标准化服务公开。该节点支持创建 MCP 兼容的服务器，可以被 LLM 客户端和其他应用程序访问以执行工具和访问资源。

## 功能特性

- **工具注册**：注册和公开 Python 函数作为 MCP 工具
- **MCP 协议兼容**：完全兼容模型上下文协议规范
- **功能发现**：自动工具发现和元数据生成
- **实时通信**：内置服务器功能用于处理 MCP 请求
- **MOFA 集成**：与 MOFA 代理框架无缝集成
- **示例工具**：用于演示的预构建数学函数

## 安装

以开发模式安装包：

```bash
pip install -e .
```

## 配置

### 输入参数

该节点作为服务器运行，不需要传统的输入参数。它会：
- 在启动时自动注册工具
- 监听 MCP 协议请求
- 响应来自 MCP 客户端的工具执行请求

### 可用工具

该节点预注册了示例工具：

| 工具 | 参数 | 描述 |
|------|------|------|
| `add` | `a: int, b: int` | 相加两个数字并返回结果 |
| `multiply` | `a: int, b: int` | 相乘两个数字（实现为 `a * add(a,b)`） |

## 使用示例

### 基本数据流配置

```yaml
# mcp-server-dataflow.yml
nodes:
  - id: mcp-server
    build: pip install -e ../../agent-hub/mcp-server
    path: mcp-server
    inputs:
      tick: dora/timer/millis/20
    env:
      MCP: true
```

### 运行节点

1. **启动 MOFA 框架：**
   ```bash
   dora up
   ```

2. **构建并启动数据流：**
   ```bash
   dora build mcp-server-dataflow.yml
   dora start mcp-server-dataflow.yml
   ```

3. **服务器将启动并显示：**
   ```
   开始运行mcp服务
   ```

4. **访问 MCP 服务器：**
   服务器将可供 MCP 客户端连接和工具执行请求使用。

## 代码示例

核心功能在 `main.py` 中实现：

```python
from mofa.agent_build.base.base_agent import MofaAgent, run_agent

def add(a: int, b: int) -> int:
    """相加两个数字"""
    return a + b

def multiply(a: int, b: int) -> int:
    """相乘两个数字"""
    return a * add(a, b)

@run_agent
def run(agent):
    # 向 MCP 服务器注册工具
    agent.register_mcp_tool(add)
    agent.register_mcp_tool(multiply)
    
    print('开始运行mcp服务')
    
    # 启动 MCP 服务器
    agent.run_mcp()

def main():
    agent_name = 'Mofa-Mcp'
    agent = MofaAgent(agent_name=agent_name)
    run(agent)
```

## 依赖项

- **pyarrow** (>= 5.0.0)：用于数据序列化和 arrow 格式支持
- **mcp**：用于模型上下文协议实现
- **mofa**：MOFA 框架（在 MOFA 环境中自动可用）

## 核心特性

### 工具注册系统
- **函数装饰**：从 Python 函数自动提取工具元数据
- **类型安全**：全面支持类型化的函数参数和返回值
- **文档集成**：函数文档字符串成为工具描述
- **动态注册**：工具可以在运行时注册

### MCP 协议实现
- **标准兼容**：完全实现模型上下文协议规范
- **客户端兼容性**：与任何 MCP 兼容的客户端配合使用
- **请求处理**：高效处理工具发现和执行请求
- **错误管理**：适当的错误处理和响应格式化

### 服务器架构
- **异步操作**：非阻塞服务器架构
- **并发请求**：同时处理多个客户端请求
- **资源管理**：高效的资源分配和清理
- **可扩展设计**：支持多个工具和高请求量

## MCP 协议概述

模型上下文协议（MCP）是向 AI 系统公开工具和资源的标准：

### 工具发现
```json
{
  "method": "tools/list",
  "params": {}
}
```

### 工具执行
```json
{
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": {
      "a": 5,
      "b": 3
    }
  }
}
```

## 自定义工具开发

### 添加新工具

```python
def divide(a: float, b: float) -> float:
    """带错误处理的除法"""
    if b == 0:
        raise ValueError("不允许除以零")
    return a / b

def get_system_info() -> dict:
    """获取系统信息"""
    import platform
    return {
        "system": platform.system(),
        "python_version": platform.python_version(),
        "machine": platform.machine()
    }

@run_agent
def run(agent):
    # 注册现有工具
    agent.register_mcp_tool(add)
    agent.register_mcp_tool(multiply)
    
    # 注册新的自定义工具
    agent.register_mcp_tool(divide)
    agent.register_mcp_tool(get_system_info)
    
    print('MCP 服务器运行中，包含自定义工具')
    agent.run_mcp()
```

### 工具要求
- 函数必须为参数提供适当的类型提示
- 返回类型应该是 JSON 可序列化的
- 为工具描述包含全面的文档字符串
- 使用适当的异常优雅地处理错误

## 使用场景

### AI 助手集成
- **LLM 工具访问**：为 AI 助手提供执行计算的工具
- **函数库**：向 AI 系统公开实用函数
- **自定义功能**：为专门的 AI 应用程序添加特定领域的工具
- **工作流集成**：使 AI 系统能够与业务流程交互

### 微服务架构
- **服务发现**：工具成为分布式系统中的可发现服务
- **API 标准化**：访问各种功能的一致接口
- **互操作性**：跨服务通信的标准协议
- **模块化**：具有清晰接口的独立工具服务

### 开发和测试
- **快速原型**：快速公开函数用于测试和开发
- **API 模拟**：为测试 AI 集成创建模拟服务
- **工具验证**：在受控环境中测试工具实现
- **集成测试**：验证 AI 系统与工具的交互

## 高级配置

### 服务器自定义
```python
class CustomMCPAgent(MofaAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_custom_tools()
    
    def setup_custom_tools(self):
        # 注册特定领域的工具
        self.register_mcp_tool(self.business_logic_tool)
        self.register_mcp_tool(self.data_processing_tool)
    
    def business_logic_tool(self, data: dict) -> dict:
        """处理业务逻辑"""
        # 自定义业务逻辑实现
        return {"processed": True, "result": data}
```

### 错误处理
```python
def safe_divide(a: float, b: float) -> dict:
    """安全除法，包含错误报告"""
    try:
        if b == 0:
            return {"error": "除以零", "result": None}
        return {"error": None, "result": a / b}
    except Exception as e:
        return {"error": str(e), "result": None}
```

## 客户端集成

### MCP 客户端示例
```python
import asyncio
from mcp_client import ClientSession

async def use_mcp_tools():
    async with ClientSession("stdio://mcp-server") as session:
        # 初始化连接
        await session.initialize()
        
        # 列出可用工具
        tools = await session.list_tools()
        print("可用工具:", [tool.name for tool in tools])
        
        # 调用工具
        result = await session.call_tool("add", arguments={"a": 5, "b": 3})
        print("加法结果:", result)
        
        # 调用另一个工具
        result = await session.call_tool("multiply", arguments={"a": 4, "b": 6})
        print("乘法结果:", result)

# 运行客户端
asyncio.run(use_mcp_tools())
```

## 故障排除

### 常见问题
1. **服务器未启动**：检查 MCP 环境变量是否设置为 true
2. **工具注册错误**：验证函数类型提示和文档字符串
3. **客户端连接问题**：确保服务器正在运行并且可访问
4. **工具执行失败**：检查函数实现和错误处理

### 调试技巧
- 启用详细日志记录以监控工具注册和执行
- 在将工具注册到 MCP 之前独立测试工具
- 验证 MCP 客户端兼容性和协议版本
- 监控负载下的服务器性能

## 性能考虑

### 可扩展性
- **工具复杂性**：保持工具实现高效以处理并发请求
- **资源使用**：监控高负载下的内存和 CPU 使用情况
- **连接管理**：为多个客户端实现适当的连接池
- **错误恢复**：实现客户端断开连接的优雅处理

### 优化
- **缓存**：为昂贵的工具操作实现缓存
- **异步操作**：为 I/O 绑定操作使用 async/await 模式
- **负载均衡**：考虑多个服务器实例以实现高可用性
- **监控**：实现服务器健康的指标和监控

## 贡献

1. 遵循既定模式添加新工具
2. 使用各种输入类型彻底测试工具
3. 确保适当的错误处理和文档
4. 验证新功能的 MCP 协议兼容性

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 链接

- [MOFA 框架](https://mofa.ai/)
- [MOFA 文档](https://github.com/moxin-org/mofa/blob/main/README.md)
- [模型上下文协议](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)