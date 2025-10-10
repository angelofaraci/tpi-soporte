import os
from typing import Optional, Tuple

# OpenAI SDK v1.x
try:
    from openai import OpenAI
except Exception:  # Library not installed yet or runtime import error
    OpenAI = None  # type: ignore


SYSTEM_PROMPT = (
    "You are a helpful music expert. Given album metadata, write a concise, factual, 2-3 sentence description. "
    "Focus on genre, style, themes, notable production, and critical reception if known. "
    "If there isn't enough information about the specific album (not the artist generally), respond with exactly: 'NO_INFO'."
)


def _build_user_prompt(album_title: str, artist: Optional[str], year: Optional[str], genres: Optional[list], styles: Optional[list]) -> str:
    parts = [f"Album title: {album_title}"]
    if artist:
        parts.append(f"Artist: {artist}")
    if year:
        parts.append(f"Year: {year}")
    if genres:
        parts.append(f"Genres: {', '.join(genres)}")
    if styles:
        parts.append(f"Styles: {', '.join(styles)}")
    parts.append("Task: Provide a brief 2-3 sentence description of this specific album. If not enough reliable info exists for this album itself, reply with 'NO_INFO'.")
    return "\n".join(parts)


def generate_album_description(album_title: str, artist: Optional[str] = None, year: Optional[str] = None,
                               genres: Optional[list] = None, styles: Optional[list] = None) -> Tuple[bool, str]:
    """
    Returns tuple (has_info, message).
    - If has_info is True, message is the generated description.
    - If has_info is False, message is a user-facing notice that the model lacks info.
    The result is not persisted anywhere; caller decides how to display it.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key or OpenAI is None:
        # Graceful fallback if SDK missing or key not configured
        return False, "AI description is unavailable: missing API key or SDK."

    try:
        client = OpenAI(api_key=api_key)
        user_prompt = _build_user_prompt(album_title, artist, year, genres, styles)

        # Using Responses API for text output with reasoning models if configured
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=220,
        )

        text = (resp.choices[0].message.content or "").strip()
        if text == "NO_INFO":
            return False, "No specific information found for this album."
        return True, text
    except Exception:
        # Do not leak details to end users
        return False, "AI description request failed. Please try again later."
