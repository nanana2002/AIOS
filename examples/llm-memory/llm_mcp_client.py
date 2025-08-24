import os
import json
import asyncio
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastmcp import Client
from openai import OpenAI


class SyncMCPClient:
    """同步 MCP 客户端 - 基于 FastMCP 官方客户端"""

    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = os.getenv('MCP_BASE_URL', 'http://127.0.0.1:9000/mcp/')
        self.base_url = base_url
        print(f"🔗 FastMCP 服务器地址: {self.base_url}")

    def _run_async(self, coro):
        """运行异步函数的辅助方法"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)

    async def _list_tools_async(self) -> List[Dict[str, Any]]:
        """异步获取工具列表"""
        mcp_client = Client(self.base_url)

        async with mcp_client:
            tools = await mcp_client.list_tools()

            # 将工具对象转换为字典
            tool_list = []
            for tool in tools:
                tool_dict = {
                    'name': getattr(tool, 'name', None),
                    'description': getattr(tool, 'description', ''),
                    'inputSchema': getattr(tool, 'inputSchema', {})
                }
                tool_list.append(tool_dict)

            return tool_list

    async def _call_tool_async(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """异步调用工具"""
        mcp_client = Client(self.base_url)

        async with mcp_client:
            try:
                tool_result_obj = await mcp_client.call_tool(tool_name, args)
                return tool_result_obj.data if tool_result_obj else {}
            except Exception as e:
                return {"error": str(e)}

    def list_tools(self) -> List[Dict[str, Any]]:
        """同步获取工具列表"""
        return self._run_async(self._list_tools_async())

    def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """同步调用工具"""
        return self._run_async(self._call_tool_async(tool_name, args))

    def close(self):
        """关闭会话（兼容性方法）"""
        pass


def format_tools_for_llm(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """将 MCP 工具格式化为 LLM 可用的工具定义"""
    tool_defs = []

    for tool in tools:
        tool_name = tool.get('name')
        if not tool_name:
            continue

        tool_description = tool.get('description', "")
        if not isinstance(tool_description, str):
            tool_description = str(tool_description)

        tool_parameters = tool.get('inputSchema')
        if not tool_parameters:
            tool_parameters = {"type": "object", "properties": {}}
        elif isinstance(tool_parameters, str):
            try:
                tool_parameters = json.loads(tool_parameters)
            except json.JSONDecodeError:
                continue
        elif not isinstance(tool_parameters, dict):
            continue

        # 确保 tool_parameters 包含 'type' 和 'properties' 键
        tool_parameters.setdefault("type", "object")
        tool_parameters.setdefault("properties", {})

        tool_defs.append({
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_description,
                "parameters": tool_parameters,
            }
        })

    return tool_defs


def chat_with_tools(user_query: str, mcp_client: SyncMCPClient,
                    tool_defs: List[Dict[str, Any]],
                    messages: List[Dict[str, Any]],
                    planner_llm: OpenAI,
                    model_name: str) -> str:
    """处理单次对话，可能涉及工具调用"""

    messages.append({"role": "user", "content": user_query})

    try:
        if tool_defs:
            plan_resp = planner_llm.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tool_defs,
                tool_choice="auto"
            )
        else:
            plan_resp = planner_llm.chat.completions.create(
                model=model_name,
                messages=messages
            )
    except Exception as e:
        messages.pop()  # 移除最后一条用户消息
        return f"错误：LLM 调用失败: {e}"

    llm_message = plan_resp.choices[0].message
    messages.append(llm_message)

    if llm_message.tool_calls:
        print(f"\n🔧 LLM 决定调用 {len(llm_message.tool_calls)} 个工具")

        # LLM 决定调用工具
        for func_call in llm_message.tool_calls:
            tool_name = func_call.function.name
            try:
                args = json.loads(func_call.function.arguments)
                print(f"  - 调用工具: {tool_name}")
                print(f"  - 参数: {args}")

                tool_result = mcp_client.call_tool(tool_name, args)
                print(f"  - 结果: {tool_result}")

                # 将工具调用结果添加到对话历史
                messages.append({
                    "role": "tool",
                    "tool_call_id": func_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })

            except json.JSONDecodeError as e:
                messages.pop()  # 移除用户消息
                messages.pop()  # 移除 LLM 的工具调用
                return f"错误：解析工具参数失败: {e}"
            except Exception as e:
                messages.pop()  # 移除用户消息
                messages.pop()  # 移除 LLM 的工具调用
                return f"错误：工具 {tool_name} 调用失败: {e}"

        # 再次调用 LLM，让它根据工具结果给出最终回复
        try:
            final_resp = planner_llm.chat.completions.create(
                model=model_name,
                messages=messages
            )

            final_content = final_resp.choices[0].message.content
            messages.append({"role": "assistant", "content": final_content})
            return final_content
        except Exception as e:
            return f"错误：生成最终回复失败: {e}"
    else:
        # LLM 决定不调用工具，直接回复
        return llm_message.content


def run_chat(user_query: str, planner_llm: OpenAI, model_name: str) -> Dict[str, Any]:
    """运行单次对话"""

    # MCP 客户端连接
    mcp_client = SyncMCPClient()

    try:
        # 获取工具列表
        print("📡 正在获取工具列表...")
        tools = mcp_client.list_tools()
        print(f"📋 发现 {len(tools)} 个工具")

        if tools:
            for tool in tools:
                print(f"  - {tool.get('name', '未知')}: {tool.get('description', '无描述')}")
        else:
            print("⚠️  未发现任何工具，将进行普通对话")

        # 构造 LLM 可用的 tool_def 列表
        tool_defs = format_tools_for_llm(tools)
        print(f"🔧 格式化 {len(tool_defs)} 个工具定义")

        # 对话历史，包括系统消息
        messages = [{
            "role": "system",
            "content": "你是一个智能 agent，可以决定是否调用相关工具来完成任务。你会根据用户的问题进行回复或工具调用。"
        }]

        # 执行单次任务
        print(f"\n💭 处理用户查询: {user_query}")
        response = chat_with_tools(user_query, mcp_client, tool_defs, messages, planner_llm, model_name)

        return {
            "query": user_query,
            "response": response,
            "tools_available": len(tool_defs),
            "success": True
        }

    except Exception as e:
        print(f"❌ 执行过程中出现错误: {e}")
        return {
            "query": user_query,
            "error": str(e),
            "success": False
        }
    finally:
        mcp_client.close()


def main():
    """主函数 - 测试用"""
    print("🚀 启动 FastMCP 客户端测试")

    # 加载环境变量
    load_dotenv('.env')

    # 配置环境变量
    os.environ['OPENAI_API_KEY'] = os.getenv('LLM_API_KEY')

    # 设置代理配置
    no_proxy = os.getenv('NO_PROXY', 'localhost,127.0.0.1')
    os.environ['NO_PROXY'] = no_proxy

    # 获取模型名称
    model_name = os.getenv('OLLAMA_MODEL_NAME', 'gpt-4o')
    print(f"🤖 使用模型: {model_name}")

    # 初始化 OpenAI 客户端
    try:
        planner_llm = OpenAI()
        print("✅ OpenAI 客户端初始化成功")
    except Exception as e:
        print(f"❌ OpenAI 客户端初始化失败: {e}")
        return

    # 测试单次查询
    test_queries = [
        "当前Ai Agent有哪些知名的开源框架"
    ]

    for query in test_queries:
        print(f"\n{'=' * 50}")
        result = run_chat(query, planner_llm, model_name)

        if result["success"]:
            print(f"✅ 查询成功")
            print(f"🔍 查询: {result['query']}")
            print(f"💬 回复: {result['response']}")
            print(f"🔧 可用工具数: {result['tools_available']}")
        else:
            print(f"❌ 查询失败")
            print(f"🔍 查询: {result['query']}")
            print(f"⚠️  错误: {result['error']}")

        print("-" * 50)

    # 交互式测试
    print(f"\n{'=' * 50}")
    print("🎯 进入交互模式 (输入 'quit' 退出)")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n用户: ").strip()
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break

            if not user_input:
                continue

            result = run_chat(user_input, planner_llm, model_name)

            if result["success"]:
                print(f"Agent: {result['response']}")
            else:
                print(f"❌ 错误: {result['error']}")

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 意外错误: {e}")


if __name__ == "__main__":
    main()