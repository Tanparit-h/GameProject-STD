import os
import asyncio
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
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

    designer = AssistantAgent(
        name="designer",
        model_client=model_client,
        system_message=(
            "You are a game designer. "
            "Create short, practical gameplay specs."
        ),
    )

    reviewer = AssistantAgent(
        name="reviewer",
        model_client=model_client,
        system_message=(
            "You are a strict reviewer. "
            "Find missing requirements and edge cases. "
            "Be concise."
        ),
    )

    team = RoundRobinGroupChat(
        participants=[designer, reviewer],
        termination_condition=MaxMessageTermination(4),
    )

    result = await team.run(
        task=(
            "Design a simple interact system: player presses E near an object. "
            "Keep it small for Unity prototype."
        )
    )

    for message in result.messages:
        print("\n==============================")
        print(f"{message.source}:")
        print(message.content)

    await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())