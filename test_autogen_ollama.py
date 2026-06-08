import os
import asyncio
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient

load_dotenv()

async def main():
    model_client = OllamaChatCompletionClient(
        model=os.getenv("MODEL_NAME", "qwen3:14b"),
        host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        options={
            "temperature": 0.2,
            "num_ctx": 8192,
        },
    )

    agent = AssistantAgent(
        name="unity_programmer_test",
        model_client=model_client,
        system_message=(
            "You are a Unity C# programmer. "
            "Answer briefly and directly."
        ),
    )

    result = await agent.run(
        task=(
            "Create a tiny Unity MonoBehaviour script named RotateObject. "
            "Return only the C# code."
        )
    )

    print(result.messages[-1].content)

    await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())