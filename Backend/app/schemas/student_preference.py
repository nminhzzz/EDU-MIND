from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

from enum import Enum

class StudyTimeEnum(str, Enum):
    morning = "morning"
    afternoon = "afternoon"
    evening = "evening"

class StudentPreferenceBase(BaseModel):
    study_hours_per_day: int = Field(2, ge=1, le=24, description="Số giờ học mong muốn mỗi ngày")
    preferred_study_time: StudyTimeEnum = Field(StudyTimeEnum.evening, description="Khung giờ học ưa thích")
    available_schedule: Dict[str, Any] = Field(
        default_factory=lambda: {
            "mon": True, "tue": True, "wed": True, "thu": True, "fri": True,
            "sat": False, "sun": False
        },
        description="Lịch rảnh theo các ngày trong tuần"
    )


class StudentPreferenceUpdate(BaseModel):
    study_hours_per_day: Optional[int] = Field(None, ge=1, le=24)
    preferred_study_time: Optional[StudyTimeEnum] = None
    available_schedule: Optional[Dict[str, bool]] = None

class StudentPreferenceResponse(StudentPreferenceBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True
