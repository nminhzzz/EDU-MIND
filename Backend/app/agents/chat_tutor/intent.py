import re
from typing import Any, Dict, Optional

PATTERN_EXPLAIN_QUIZ = re.compile(
    r"(gi(ả|a)i\s+thích\s+(câu\s+sai|bài\s+thi|bài\s+quiz|k(ế|e)t\s+qu(ả|a)|l(ỗ|o)i|đáp\s+án))|"
    r"(t(ạ|a)i\s+sao\s+(đáp\s+án|sai|đúng|câu|tôi\s+sai|chọn|lựa\s+chọn))|"
    r"(xem\s+l(ỗ|o)i\s+sai)|"
    r"(gi(ả|a)i\s+thích\s+bài\s+làm)|"
    r"(phân\s+tích\s+bài\s+thi)|"
    r"(\bbài\s+ki(ể|m)\s+tra\b.*?\b(vừa\s+làm|vừa\s+nộp|sai|k(ế|e)t\s+qu(ả|a))\b)|"
    r"(\b(l(ỗ|o)i\s+sai|câu\s+sai|sai\s+ở\s+đâu)\b)",
    re.IGNORECASE,
)


async def detect_intent(
    message: str, session_id: Optional[str] = None, student_id: Optional[int] = None
) -> Dict[str, Any]:
    msg_lower = message.lower()

    if PATTERN_EXPLAIN_QUIZ.search(msg_lower):
        return {"type": "explain_quiz", "data": {}}

    return {"type": "chat", "data": {}}
