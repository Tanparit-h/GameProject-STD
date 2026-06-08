import os
from pathlib import Path
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]

def _read_prompt(name: str) -> str:
    return (ROOT / "prompts" / name).read_text(encoding="utf-8")

def _create_model_client() -> OllamaChatCompletionClient:
    return OllamaChatCompletionClient(
        model=os.getenv("MODEL_NAME", "qwen3:14b"),
        host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        options={
            "temperature": 0.2,
            "num_ctx": 8192,
        },
    )

async def run_role(
    role_name: str,
    prompt_file: str,
    task: str,
) -> str:
    model_client = _create_model_client()

    agent = AssistantAgent(
        name=role_name,
        model_client=model_client,
        system_message=_read_prompt(prompt_file),
    )

    result = await agent.run(task=task)

    await model_client.close()

    return str(result.messages[-1].content)