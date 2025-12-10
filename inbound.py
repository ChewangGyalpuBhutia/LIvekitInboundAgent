import asyncio
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent
from livekit.plugins import openai
from openai.types.beta.realtime.session import TurnDetection
from instructions import INBOUND_INSTRUCTIONS

# Load environment variables
load_dotenv()


class InboundAssistant(Agent):
    """AI Agent for handling inbound phone calls"""

    def __init__(self, instructions: str) -> None:
        super().__init__(instructions=instructions)


async def entrypoint(ctx: agents.JobContext):
    """Entrypoint for inbound phone calls"""

    # Connect to the room
    await ctx.connect()

    # Wait for SIP participant to connect
    for _ in range(30):
        if len(ctx.room.remote_participants) > 0:
            break
        await asyncio.sleep(1)
    else:
        return

    await asyncio.sleep(1.5)

    # Get instructions from instructions.py
    instructions = INBOUND_INSTRUCTIONS

    # Create agent session with OpenAI Realtime
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="ballad",
            temperature=0.8,
        )
    )

    # Start the session with the custom agent
    await session.start(
        room=ctx.room, agent=InboundAssistant(instructions=instructions)
    )


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint, agent_name="twilio-inbound-agent"
        )
    )
