import json
import logging
import os

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    room_io,
)
from livekit.agents.beta.tools import EndCallTool
from livekit.plugins import openai
# from livekit.plugins import ai_coustics
from openai.types.beta.realtime.session import TurnDetection

from agents.admissions_agent import create_admissions_agent
from agents.course_agent import create_course_agent
from agents.faq_agent import create_faq_agent
from config.helper import get_university_context
from config.models import RealtimeConfig, TurnDetectionConfig
from prompts.main_prompt import MAIN_PROMPT
from tools.router_tools import (
    make_transfer_to_admissions_agent_tool,
    make_transfer_to_course_agent_tool,
    make_transfer_to_faq_agent_tool,
)
from hooks.call_tracker import CallTracker

logger = logging.getLogger("main_agent")

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env.local"))

DEFAULT_UNIVERSITY_PHONE = os.getenv("UNIVERSITY_PHONE", "+14843174117")

server = AgentServer()


def prewarm(proc: JobProcess):
    pass


server.setup_fnc = prewarm


def _extract_called_number(ctx: JobContext) -> str:
    """Resolve the called phone number from LiveKit SIP job/room metadata."""
    try:
        if hasattr(ctx, "job") and ctx.job:
            metadata = getattr(ctx.job, "metadata", None)
            if isinstance(metadata, str) and metadata.strip().startswith("{"):
                try:
                    metadata = json.loads(metadata)
                except (ValueError, TypeError):
                    pass
            if isinstance(metadata, dict):
                return (
                    metadata.get("to_number")
                    or metadata.get("to")
                    or metadata.get("called_number")
                    or metadata.get("phone_number")
                    or DEFAULT_UNIVERSITY_PHONE
                )
        if hasattr(ctx, "room") and ctx.room:
            room_metadata = getattr(ctx.room, "metadata", None)
            if room_metadata:
                return room_metadata
    except Exception as e:
        logger.warning(f"Could not extract called number: {e}")
    return DEFAULT_UNIVERSITY_PHONE


@server.rtc_session(agent_name="Universities Voice Agent")
async def main_agent(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    university_phone = _extract_called_number(ctx)
    logger.info(f"Using university phone: {university_phone}")

    context = await get_university_context(university_phone)

    # --- call tracking add-on (observability only) ---
    tracker = CallTracker()
    await tracker.start(
        room_name=ctx.room.name,
        university_id=str(context.get("university_id")) if context.get("university_id") else None,
        caller_identity=getattr(ctx.room, "metadata", None),
    )

    async def _on_shutdown():
        await tracker.end()

    ctx.add_shutdown_callback(_on_shutdown)
    # -------------------------------------------------

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model=RealtimeConfig.MODEL.value,
            speed=RealtimeConfig.SPEED.value,
            turn_detection=TurnDetection(
                type=TurnDetectionConfig.TYPE.value,
                threshold=TurnDetectionConfig.THRESHOLD.value,
                prefix_padding_ms=TurnDetectionConfig.PREFIX_PADDING_MS.value,
                silence_duration_ms=TurnDetectionConfig.SILENCE_DURATION_MS.value,
                create_response=TurnDetectionConfig.CREATE_RESPONSE.value,
                interrupt_response=TurnDetectionConfig.INTERRUPT_RESPONSE.value,
            ),
        ),
    )

    agents: dict = {}

    admissions_agent = create_admissions_agent(context, session, agents)
    course_agent = create_course_agent(context, session, agents)
    faq_agent = create_faq_agent(context, session, agents)

    main_router = Agent(
        instructions=MAIN_PROMPT.format(university_name=context["university_name"]),
        tools=[
            EndCallTool(),
            make_transfer_to_admissions_agent_tool(session, agents),
            make_transfer_to_course_agent_tool(session, agents),
            make_transfer_to_faq_agent_tool(session, agents),
        ],
    )

    agents["admissions"] = admissions_agent
    agents["course"] = course_agent
    agents["faq"] = faq_agent
    agents["main"] = main_router

    # --- message logging add-on ---
    try:
        @session.on("conversation_item_added")
        def _on_conversation_item(item):
            role = str(getattr(item, "role", "unknown"))
            text = str(getattr(item, "text_content", None) or getattr(item, "text", None) or "")
            if text:
                import asyncio as _asyncio  # noqa: PLC0415
                _asyncio.ensure_future(tracker.log_message(role, text))
    except Exception as _e:
        logger.warning(f"Could not attach call tracker listener: {_e}")
    # ------------------------------

    await ctx.connect()

    await session.start(
        agent=main_router,
        room=ctx.room,
        room_options=room_io.RoomOptions(
            # audio_input=room_io.AudioInputOptions(
            #     noise_cancellation=ai_coustics.audio_enhancement(
            #         model=ai_coustics.EnhancerModel.QUAIL_VF_L,
            #         model_parameters=ai_coustics.ModelParameters(enhancement_level=0.8),
            #     ),
            # ),
        ),
    )


if __name__ == "__main__":
    cli.run_app(server)
