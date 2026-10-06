from enum import Enum
from dataclasses import dataclass


@dataclass
class VoiceOption:
    id: str
    label: str
    provider: str
    gender: str
    accent: str


VOICE_OPTIONS: list[VoiceOption] = [
    # Cartesia — British
    VoiceOption("gemma",       "Gemma — Decisive British female",       "cartesia", "female",  "British"),
    VoiceOption("lucy",        "Lucy — Reassuring British female",       "cartesia", "female",  "British"),
    VoiceOption("victoria",    "Victoria — Crisp British female",        "cartesia", "female",  "British"),
    VoiceOption("evie",        "Evie — Formal British female",           "cartesia", "female",  "British"),
    # Cartesia — American
    VoiceOption("jackqueline", "Jackqueline — American female",          "cartesia", "female",  "American"),
    VoiceOption("cathy",       "Cathy — American female",                "cartesia", "female",  "American"),
    VoiceOption("dorothy",     "Dorothy — American female",              "cartesia", "female",  "American"),
    # Deepgram — Female
    VoiceOption("asteria",     "Asteria — Warm professional female",     "deepgram", "female",  "American"),
    VoiceOption("luna",        "Luna — Soft friendly female",            "deepgram", "female",  "American"),
    VoiceOption("stella",      "Stella — Upbeat cheerful female",        "deepgram", "female",  "American"),
    VoiceOption("athena",      "Athena — Warm conversational female",    "deepgram", "female",  "American"),
    VoiceOption("hera",        "Hera — Rich welcoming female",           "deepgram", "female",  "American"),
    # Deepgram — Male
    VoiceOption("orion",       "Orion — Warm friendly male",             "deepgram", "male",    "American"),
    VoiceOption("arcas",       "Arcas — Smooth approachable male",       "deepgram", "male",    "American"),
    VoiceOption("perseus",     "Perseus — Clear pleasant male",          "deepgram", "male",    "American"),
    # OpenAI Realtime
    VoiceOption("marin",       "Marin — Warm and clear",                 "openai",   "neutral", "American"),
    VoiceOption("alloy",       "Alloy — Neutral balanced",               "openai",   "neutral", "American"),
    VoiceOption("ash",         "Ash — Smooth and steady",                "openai",   "male",    "American"),
    VoiceOption("coral",       "Coral — Warm and conversational",        "openai",   "female",  "American"),
    VoiceOption("echo",        "Echo — Clear and confident",             "openai",   "male",    "American"),
    VoiceOption("sage",        "Sage — Calm and thoughtful",             "openai",   "neutral", "American"),
    VoiceOption("shimmer",     "Shimmer — Bright and energetic",         "openai",   "female",  "American"),
    VoiceOption("verse",       "Verse — Dynamic and engaging",           "openai",   "neutral", "American"),
    VoiceOption("cedar",       "Cedar — Deep and grounded",              "openai",   "male",    "American"),
]


_PERSONALITY_LABELS: dict[str, str] = {
    "friendly":     "Warm & welcoming",
    "professional": "Quick & efficient",
    "casual":       "Playful & casual",
    "formal":       "Polished & formal",
    "enthusiastic": "Energetic & enthusiastic",
}


class AgentPersonality(Enum):
    FRIENDLY     = "friendly"
    PROFESSIONAL = "professional"
    CASUAL       = "casual"
    FORMAL       = "formal"
    ENTHUSIASTIC = "enthusiastic"

    @classmethod
    def list(cls):
        return [v.value for v in cls]

    @classmethod
    def default(cls):
        return cls.FRIENDLY


class CARTESIA_TTS(Enum):
    # American accents
    JACKQUELINE = "9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
    CATHY = "e8e5fffb-252c-436d-b842-8879b84445b6"
    DOROTHY = "66c6b81c-ddb7-4892-bdd5-19b5a7be38e7"
    # UK accents
    GEMMA    = "62ae83ad-4f6a-430b-af41-a9bede9286ca"
    LUCY     = "2f251ac3-89a9-4a77-a452-704b474ccd01"
    VICTORIA = "dc30854e-e398-4579-9dc8-16f6cb2c19b9"
    EVIE     = "e5d4c33a-d8f6-46e8-a10f-b5afecc35648"

    MODEL = "sonic-3"
    SPEED = 0.9
    EMOTION = ["positivity:high", "curiosity:high"]

    @classmethod
    def list(cls):
        return [v.value for v in cls if v not in (cls.MODEL, cls.SPEED, cls.EMOTION)]

    @classmethod
    def default(cls):
        return cls.GEMMA


class OPENAI_REALTIME_VOICES(Enum):
    ALLOY = "alloy"
    MARIN = "marin"
    CEDAR = "cedar"

    @classmethod
    def default(cls):
        return cls.MARIN


class OPENAI_REALTIME_MODELS(Enum):
    GPT_REALTIME = "gpt-realtime"
    GPT_REALTIME_MINI_2025_12_15 = "gpt-realtime-mini-2025-12-15"

    @classmethod
    def default(cls):
        return cls.GPT_REALTIME_MINI_2025_12_15


class RealtimeConfig(Enum):
    VOICE = OPENAI_REALTIME_VOICES.default().value
    MODEL = OPENAI_REALTIME_MODELS.default().value
    SPEED = 0.9


class TurnDetectionConfig(Enum):
    TYPE = "server_vad"
    THRESHOLD = 0.7
    PREFIX_PADDING_MS = 300
    SILENCE_DURATION_MS = 300
    CREATE_RESPONSE = True
    INTERRUPT_RESPONSE = True
