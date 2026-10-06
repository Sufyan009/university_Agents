import logging

from livekit.agents import Agent, AgentSession
from livekit.agents.beta.tools import EndCallTool

from prompts.course_prompt import COURSE_PROMPT
from agents._personality import personality_desc, special_instructions_section
from tools.info_tools import (
    make_get_course_detail_tool,
    make_list_courses_tool,
    make_list_subjects_tool,
)
from tools.router_tools import (
    make_transfer_to_admissions_agent_tool,
    make_transfer_to_faq_agent_tool,
    make_transfer_to_main_agent_tool,
)

logger = logging.getLogger("course_agent")


class CourseAgent(Agent):
    async def on_enter(self) -> None:
        await self.session.generate_reply()


def create_course_agent(context: dict, session: AgentSession, agents: dict) -> Agent:
    university_id = context["university_id"]
    return CourseAgent(
        instructions=COURSE_PROMPT.format(
            university_name=context["university_name"],
            personality_desc=personality_desc(context),
            courses_text=context.get("courses_text") or "Course list is being updated.",
            special_instructions_section=special_instructions_section(context),
        ),
        tools=[
            EndCallTool(),
            make_transfer_to_admissions_agent_tool(session, agents),
            make_transfer_to_faq_agent_tool(session, agents),
            make_transfer_to_main_agent_tool(session, agents),
            make_list_courses_tool(university_id),
            make_get_course_detail_tool(university_id),
            make_list_subjects_tool(university_id),
        ],
    )
