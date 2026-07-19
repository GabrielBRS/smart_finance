from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from cognition.exemplos.agent import SYSTEM_PROMPT
from cognition.exemplos.config import LLM_MODEL, LLM_BASE_URL, LLM_API_KEY

model_client = OpenAIChatCompletionClient(
    model=LLM_MODEL, base_url=LLM_BASE_URL, api_key=LLM_API_KEY,
    model_info={"vision": False, "function_calling": True, "json_output": True, "family": "unknown"},
)

agent = AssistantAgent("cognicao", model_client=model_client, system_message=SYSTEM_PROMPT)


async def run_autogen(question: str) -> str:
    result = await agent.run(task=question)
    return result.messages[-1].content