import os
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from tools.models import University, Course, AgentConfig, AdmissionInfo
from config.models import CARTESIA_TTS, AgentPersonality, VOICE_OPTIONS


# Engine (created once per process)
_engine = None
_session_maker = None


def _get_session_maker() -> sessionmaker:
    global _engine, _session_maker
    if _session_maker is None:
        db_url = os.environ["DATABASE_URL"]
        _engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={"timeout": 10, "command_timeout": 10}
        )
        _session_maker = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _session_maker


_CARTESIA_VOICE_MAP: dict[str, str] = {
    m.name.lower(): m.value
    for m in CARTESIA_TTS
    if m not in (CARTESIA_TTS.MODEL, CARTESIA_TTS.SPEED, CARTESIA_TTS.EMOTION)
}

_VOICE_PROVIDER_MAP: dict[str, str] = {v.id: v.provider for v in VOICE_OPTIONS}


def _resolve_cartesia_voice(voice_id: str | None) -> str:
    """Map a short voice_id (e.g. 'gemma') to its Cartesia UUID, falling back to default."""
    if voice_id and _VOICE_PROVIDER_MAP.get(voice_id) == "cartesia":
        return _CARTESIA_VOICE_MAP.get(voice_id, CARTESIA_TTS.default().value)
    return CARTESIA_TTS.default().value


def _default_context() -> dict[str, Any]:
    return {
        "university_id": None,
        "university_name": "Our University",
        "profile_text": "",
        "courses_text": "",
        "admissions_text": "",
        "voice_id": CARTESIA_TTS.default().value,
        "speed": CARTESIA_TTS.SPEED.value,
        "personality": AgentPersonality.default().value,
        "greeting_message": "Hello, thanks for calling. How can I help you today?",
        "special_instructions": None,
        "enable_admissions": True,
        "enable_courses": True,
        "enable_scholarships": True,
        "enable_faq": True,
    }


async def get_university_context(phone: str) -> dict[str, Any]:
    """Return university context including agent config for the given phone number.

    Single point of tenant resolution: phone -> university_id. Every downstream
    query is scoped to that id, so a caller can never reach another university's data.
    """
    maker = _get_session_maker()
    async with maker() as session:
        result = await session.execute(select(University).where(University.phone == phone))
        university = result.scalars().first()
        if university is None:
            return _default_context()

        # Courses (compact catalog summary; detail is fetched on demand via tools)
        courses_result = await session.execute(
            select(Course).where(Course.university_id == university.id)
        )
        courses = courses_result.scalars().all()
        course_lines: list[str] = []
        for c in sorted(courses, key=lambda x: x.name):
            line = f"- {c.name}"
            extras = []
            if c.degree_type:
                extras.append(c.degree_type)
            if c.duration:
                extras.append(c.duration)
            if extras:
                line += f" ({', '.join(extras)})"
            course_lines.append(line)
        courses_text = "\n".join(course_lines)

        # Admissions summary
        adm_result = await session.execute(
            select(AdmissionInfo).where(AdmissionInfo.university_id == university.id)
        )
        admission = adm_result.scalars().first()
        admissions_parts: list[str] = []
        if admission:
            if admission.eligibility:
                admissions_parts.append(f"Eligibility: {admission.eligibility}")
            if admission.application_process:
                admissions_parts.append(f"How to apply: {admission.application_process}")
        admissions_text = "\n".join(admissions_parts)

        # Agent config
        config_result = await session.execute(
            select(AgentConfig).where(AgentConfig.university_id == university.id)
        )
        config = config_result.scalars().first()
        voice_cfg = (config.voice_config or {}) if config else {}
        raw_voice_id = voice_cfg.get("voice_id") if voice_cfg else None
        speed = voice_cfg.get("speed") if voice_cfg else None

        # Profile blurb
        profile_parts: list[str] = []
        if university.description:
            profile_parts.append(university.description)
        if university.website:
            profile_parts.append(f"Website: {university.website}")
        if university.location:
            loc = university.location
            city = loc.get("city") if isinstance(loc, dict) else None
            country = loc.get("country") if isinstance(loc, dict) else None
            where = ", ".join(p for p in [city, country] if p)
            if where:
                profile_parts.append(f"Location: {where}")

        return {
            "university_id": university.id,
            "university_name": university.name,
            "profile_text": "\n".join(profile_parts).strip(),
            "courses_text": courses_text,
            "admissions_text": admissions_text,
            "voice_id": _resolve_cartesia_voice(raw_voice_id),
            "speed": speed or CARTESIA_TTS.SPEED.value,
            "personality": (config.personality if config else None) or AgentPersonality.default().value,
            "greeting_message": (config.greeting_message if config else None)
            or f"Hello, thanks for calling {university.name}. How can I help you today?",
            "special_instructions": config.special_instructions if config else None,
            "enable_admissions": config.enable_admissions if config else True,
            "enable_courses": config.enable_courses if config else True,
            "enable_scholarships": config.enable_scholarships if config else True,
            "enable_faq": config.enable_faq if config else True,
        }
