from livekit.agents import AgentSession, function_tool


def make_transfer_to_admissions_agent_tool(session: AgentSession, agents: dict):
    @function_tool
    async def transfer_to_admissions_agent() -> str:
        """Transfer the caller to the admissions agent.

        Call this for questions about admission criteria, eligibility, deadlines,
        the application process, required documents, or scholarships.
        """
        session.update_agent(agents["admissions"])
        return "One moment, connecting you to our admissions team."

    return transfer_to_admissions_agent


def make_transfer_to_course_agent_tool(session: AgentSession, agents: dict):
    @function_tool
    async def transfer_to_course_agent() -> str:
        """Transfer the caller to the courses agent.

        Call this for questions about courses, degrees, subjects, modules,
        fees, course duration, or course-specific entry requirements.
        """
        session.update_agent(agents["course"])
        return "One moment, connecting you to someone who can help with course details."

    return transfer_to_course_agent


def make_transfer_to_faq_agent_tool(session: AgentSession, agents: dict):
    @function_tool
    async def transfer_to_faq_agent() -> str:
        """Transfer the caller to the general information agent.

        Call this for campus information, student services, and general questions
        that are not specifically about admissions or courses.
        """
        session.update_agent(agents["faq"])
        return "One moment, connecting you to general information."

    return transfer_to_faq_agent


def make_transfer_to_main_agent_tool(session: AgentSession, agents: dict):
    @function_tool
    async def transfer_to_main_agent() -> str:
        """Transfer the caller back to the main agent.

        Call this when the caller wants something outside your specialty.
        """
        session.update_agent(agents["main"])
        return "One moment, transferring you back."

    return transfer_to_main_agent
