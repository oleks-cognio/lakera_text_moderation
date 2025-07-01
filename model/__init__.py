from typing import TypedDict, List, cast
from transformers import pipeline

class ScoreEntry(TypedDict):
    label: str
    score: float

moderator = pipeline(
    task="text-classification",
    model="KoalaAI/Text-Moderation",
    top_k=None
)

def moderate(text: str) -> dict[str, float]:
    """Run moderation on a text and return a mapping of raw labels to scores."""
    try:
        output = cast(List[List[ScoreEntry]], moderator(text))
    except Exception as e:
        raise RuntimeError(f"Moderation inference failed: {e}")

    scores = output[0]
    return {entry["label"]: entry["score"] for entry in scores}