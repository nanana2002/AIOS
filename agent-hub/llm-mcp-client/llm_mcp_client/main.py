import os
import json
import requests
from typing import List, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI
from mofa.agent_build.base.base_agent import MofaAgent, run_agent


class SyncMCPClient:
    """同步 MCP 客户端"""

    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = os.getenv('MCP_BASE_URL', 'http://127.0.0.1:9000/mcp/')
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def list_tools(self) -> List[Dict[str, Any]]:
        """获取工具列表"""
        try:
            response = self.session.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取工具列表失败: {e}")
            return []

    def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        try:
            payload = {
                "name": tool_name,
                "arguments": args
            }
            response = self.session.post(f"{self.base_url}/call_tool", json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("data", {}) if isinstance(result, dict) else result
        except requests.RequestException as e:
            print(f"调用工具 {tool_name} 失败: {e}")
            return {"error": str(e)}

    def close(self):
        """关闭会话"""
        self.session.close()


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
        # LLM 决定调用工具
        for func_call in llm_message.tool_calls:
            tool_name = func_call.function.name
            try:
                args = json.loads(func_call.function.arguments)
                tool_result = mcp_client.call_tool(tool_name, args)

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


@run_agent
def run(agent: MofaAgent, planner_llm: OpenAI = None, model_name: str = None):
    """运行 MCP Agent - 单次执行模式"""

    # 获取用户输入
    user_query = agent.receive_parameter('query')
    if not user_query:
        agent.send_output(
            agent_output_name='error',
            agent_result="错误：未提供查询参数"
        )
        return

    # MCP 客户端连接
    mcp_client = SyncMCPClient()

    try:
        # 获取工具列表
        tools = mcp_client.list_tools()

        # 构造 LLM 可用的 tool_def 列表
        tool_defs = format_tools_for_llm(tools)

        # 对话历史，包括系统消息
        messages = [{
            "role": "system",
            "content": "你是一个智能 agent，可以决定是否调用相关工具来完成任务。你会根据用户的问题进行回复或工具调用。"
        }]

        # 执行单次任务
        response = chat_with_tools(user_query, mcp_client, tool_defs, messages, planner_llm, model_name)

        agent.send_output(
            agent_output_name='llm-mcp-client-result',
            agent_result={
                "query": user_query,
                "response": response,
                "tools_available": len(tool_defs)
            }
        )

    except Exception as e:
        agent.send_output(
            agent_output_name='llm-mcp-client-result',
            agent_result={
                "query": user_query,
                "error": str(e)
            }
        )
    finally:
        mcp_client.close()


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv('.env')

    # 配置环境变量
    os.environ['OPENAI_API_KEY'] = os.getenv('LLM_API_KEY')

    # 获取模型名称
    model_name = os.getenv('LLM_MODEL_NAME', 'gpt-4o')

    # 初始化 OpenAI 客户端
    planner_llm = OpenAI()

    # 创建 agent 实例
    agent = MofaAgent(agent_name='mcp-chat-agent')

    # 将 planner_llm 和 model_name 设置到 agent 上下文中

    # 运行 agent
    run(agent=agent, planner_llm=planner_llm, model_name=model_name)


if __name__ == "__main__":
    main()