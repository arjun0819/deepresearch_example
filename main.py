# -*- coding: utf-8 -*-
"""The main entry point of the Deep Research agent example."""
import asyncio
import os
from deepresearch_agent import DeepResearchAgent
from agentscope import logger
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import DashScopeChatModel
from agentscope.message import Msg
from agentscope.mcp import StdIOStatefulClient
from agentscope.mcp import HttpStatefulClient
from dotenv import load_dotenv

load_dotenv()

async def main(user_query: str) -> None:
    """The main entry point for the Deep Research agent example."""
    logger.setLevel("DEBUG")
    # tavily_search_client = HttpStatefulClient(
    # name="tavily_mcp",
    # transport="sse",
    # url="https://mcp.tavily.com/mcp/?tavilyApiKey=[api-key]"
    # )

    tavily_search_client = StdIOStatefulClient(
        name="tavily_mcp",
        command="npx",
        args=["-y", "tavily-mcp@latest"],
        env={"TAVILY_API_KEY": os.getenv("TAVILY_API_KEY", "")},
    )

    default_working_dir = os.path.join(
        os.path.dirname(__file__),
        "deepresearch_agent_demo_env",
    )

    agent_working_dir = os.getenv(
        "AGENT_OPERATION_DIR",
        default_working_dir,
    )
    os.makedirs(agent_working_dir, exist_ok=True)

    try:
        await tavily_search_client.connect()
        agent = DeepResearchAgent(
            name="Friday",
            sys_prompt="You are a helpful assistant named Friday.",
            model=DashScopeChatModel(
                api_key=os.environ.get("DASHSCOPE_API_KEY"),
                # api_key=os.getenv("DASHBOARD_API_KEY"),
                model_name="qwen-max",
                enable_thinking=False,
                stream=True,
            ),
            
            formatter=DashScopeChatFormatter(),
            memory=InMemoryMemory(),
            search_mcp_client=tavily_search_client,
            tmp_file_storage_dir=agent_working_dir,
        )
        user_name = "Bob"
        msg = Msg(
            user_name,
            content=user_query,
            role="user",
        )
        result = await agent(msg)
        logger.info(result)

    except Exception as err:
        logger.exception(err)

    finally:
        await tavily_search_client.close()

if __name__ == "__main__":
    query = "如果埃鲁德·基普乔格能够以他创纪录的马拉松配速无限期地奔跑，那么以维基百科月球页面上记载的最小近地点距离计算，他需要多少千小时才能跑完地球与月球之间的这段距离？请将计算结果四舍五入到最近的 1000 小时，且不要使用任何千位分隔符。"
    try:
        asyncio.run(main(query))
 
    except Exception as e:
        logger.exception(e)
