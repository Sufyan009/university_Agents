"""Shared personality descriptions for sub-agent prompts."""

PERSONALITY_MAP: dict[str, str] = {
    "friendly":     "Be warm, welcoming, and approachable.",
    "professional": "Be professional, efficient, and courteous.",
    "casual":       "Be laid-back and conversational.",
    "formal":       "Be polite, formal, and respectful.",
    "enthusiastic": "Be energetic, upbeat, and excited.",
}


def personality_desc(context: dict) -> str:
    return PERSONALITY_MAP.get(context.get("personality", "friendly"), "Be warm and friendly.")


def special_instructions_section(context: dict) -> str:
    return (
        f"SPECIAL INSTRUCTIONS:\n{context['special_instructions']}"
        if context.get("special_instructions")
        else ""
    )
