from __future__ import annotations


def normalize_distance(distance: float) -> float:
    """Convert a vector-store distance into a bounded confidence score."""
    if distance < 0:
        return 0.0
    if distance > 1:
        return max(0.0, 1.0 - min(distance, 1.0))
    return 1.0 - distance


def extract_qa(content: str) -> tuple[str | None, str | None]:
    question = ""
    answer = ""
    for line in (content or "").splitlines():
        if line.startswith("问题："):
            question = line.replace("问题：", "", 1).strip()
        elif line.startswith("答案："):
            answer = line.replace("答案：", "", 1).strip()
    return question or None, answer or None

