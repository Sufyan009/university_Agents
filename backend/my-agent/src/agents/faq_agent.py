import logging

from livekit.agents import Agent, AgentSession
from livekit.agents.beta.tools import EndCallTool

from prompts.faq_prompt import FAQ_PROMPT
from agents._personality import personality_desc, special_instructions_section
from tools.info_tools import make_search_faqs_tool
from tools.router_tools import (
    make_transfer_to_admissions_agent_tool,
    make_transfer_to_course_agent_tool,
    make_transfer_to_main_agent_tool,
)

logger = logging.getLogger("faq_agent")


class FAQAgent(Agent):
    async def on_enter(self) -> None:
        await self.session.generate_reply()


def create_faq_agent(context: dict, session: AgentSession, agents: dict) -> Agent:
    university_id = context["university_id"]
    return FAQAgent(
        instructions=FAQ_PROMPT.format(
            university_name=context["university_name"],
            personality_desc=personality_desc(context),
            profile_text=context.get("profile_text") or "General information is being updated.",
            special_instructions_section=special_instructions_section(context),
        ),
        tools=[
            EndCallTool(),
            make_transfer_to_admissions_agent_tool(session, agents),
            make_transfer_to_course_agent_tool(session, agents),
            make_transfer_to_main_agent_tool(session, agents),
            make_search_faqs_tool(university_id),
        ],
    )
