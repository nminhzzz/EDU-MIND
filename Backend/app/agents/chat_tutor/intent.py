import re
from typing import Optional, Dict, Any
from datetime import date
from app.agents.base import generate_content_nvidia
from app.database.redis import get_redis_client

PATTERN_CREATE_PLAN = re.compile(
    r"(l(ậ|â)p|lên|t(ạ|a)o|làm|v(ẽ|e)|d(ự|u)ng)\s*(l(ộ|o) trình|k(ế|e) ho(ạ|a)ch|k(ế|e) ho(ạ|a)ch h(ọ|o)c t(ậ|a)p)",
    re.IGNORECASE
)
PATTERN_GOAL = re.compile(
    r"(m(ụ|u)c tiêu|target|đi(ể|e)m s(ố|o)|mong mu(ố|o)n|[đd](ạ|a)t).*?(\d+(\.\d+)?)\s*(/10|đi(ể|e)m)?",
    re.IGNORECASE
)
PATTERN_DEADLINE = re.compile(
    r"(deadline|h(ạ|a)n chót|còn|trong|sau).*?(\d+)\s*(ngày|tu(ầ|a)n|tháng)",
    re.IGNORECASE
)
PATTERN_SUBJECT = re.compile(
    r"(h(ọ|o)c|môn|subject)\s+(\S+)",
    re.IGNORECASE
)
PATTERN_CONFIRM = re.compile(
    r"(lưu|l(ư|u)u l(ạ|a)i|ch(ố|o)t|confirm|ok|đ(ồ|o)ng ý|đư(ợ|o)c r(ồ|o)i|nh(ư|u) v(ậ|a)y|lưu plan|ch(ố|o)t plan)",
    re.IGNORECASE
)
PATTERN_REFINE = re.compile(
    r"(s(ử|u)a|thay đ(ổ|o)i|đi(ề|e)u ch(ỉ|i)nh|b(ớ|o)t|thêm|b(ỏ|o) b(ớ|o)t|gi(ả|a)m|tăng|ch(ỉ|i)nh|tinh ch(ỉ|i)nh|refine|update|adjust)",
    re.IGNORECASE
)
PATTERN_EXPLAIN_QUIZ = re.compile(
    r"(gi(ả|a)i thích|t(ạ|a)i sao|sao|l(ỗ|o)i sai|ch(ỉ|i) ra sai|câu sai|bài ki(ể|m) tra|quiz|n(ộ|o)p bài|k(ế|e)t qu(ả|a))",
    re.IGNORECASE
)


SUBJECT_DB = {
    "tri(ế|e|é)t h(ọ|o)c": "Triết học Mác - Lênin",
    "tri(ế|e|é)t": "Triết học Mác - Lênin",
    "toán": "Toán cao cấp",
    "toán cao c(ấ|a)p": "Toán cao cấp",
    "v(ậ|a)t lý": "Vật lý đại cương",
    "anh văn": "Tiếng Anh",
    "ti(ế|e)ng anh": "Tiếng Anh",
    "tin h(ọ|o)c": "Tin học đại cương",
    "l(ậ|a)p trình": "Tin học đại cương",
}

def extract_subject(message: str) -> Optional[str]:
    msg_lower = message.lower()
    for pattern, name in SUBJECT_DB.items():
        if re.search(pattern, msg_lower):
            return name
    match = PATTERN_SUBJECT.search(msg_lower)
    if match:
        return match.group(2).capitalize()
    return None

def extract_target_score(message: str) -> Optional[float]:
    match = PATTERN_GOAL.search(message)
    if match:
        try:
            return float(match.group(7))
        except ValueError:
            return None
    return None

def extract_deadline(message: str) -> Optional[date]:
    today = date.today()
    match = PATTERN_DEADLINE.search(message)
    if match:
        try:
            num = int(match.group(3))
            unit = match.group(3).lower()
            if "tuần" in unit or "tu" in unit:
                return date(today.year + (today.month + num * 4 - 1) // 12, (today.month + num * 4 - 1) % 12 + 1, min(today.day, 28))
            elif "tháng" in unit:
                return date(today.year + (today.month + num - 1) // 12, (today.month + num - 1) % 12 + 1, min(today.day, 28))
            else:
                return date.fromordinal(today.toordinal() + num)
        except ValueError:
            return None
    return None

def has_cached_draft(session_id: str) -> bool:
    if not session_id:
        return False
    redis_client = get_redis_client()
    return redis_client.exists(f"unified_draft:{session_id}")

async def detect_intent(
    message: str,
    session_id: Optional[str] = None,
    student_id: Optional[int] = None
) -> Dict[str, Any]:
    msg_lower = message.lower()
    has_draft = has_cached_draft(session_id)

    if has_draft and PATTERN_CONFIRM.search(msg_lower):
        return {"type": "confirm_plan", "data": {}}

    if has_draft and PATTERN_REFINE.search(msg_lower):
        return {"type": "refine_plan", "data": {"user_message": message}}

    if PATTERN_CREATE_PLAN.search(msg_lower) or PATTERN_GOAL.search(msg_lower) or PATTERN_DEADLINE.search(msg_lower):
        subject = extract_subject(message)
        score = extract_target_score(message)
        deadline = extract_deadline(message)

        missing = []
        if not subject:
            missing.append("môn học")
        if not score:
            missing.append("điểm mục tiêu")
        if not deadline:
            missing.append("thời hạn")

        if missing:
            return {
                "type": "ask_info",
                "data": {
                    "missing": missing,
                    "subject": subject,
                    "target_score": score,
                    "deadline": deadline
                }
            }

        return {
            "type": "create_plan",
            "data": {
                "subject": subject,
                "target_score": score,
                "deadline": deadline.isoformat(),
                "user_message": message
            }
        }

    if PATTERN_EXPLAIN_QUIZ.search(msg_lower):
        return {"type": "explain_quiz", "data": {}}

    return {"type": "chat", "data": {}}

