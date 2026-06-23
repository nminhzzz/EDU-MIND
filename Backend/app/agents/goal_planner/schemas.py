from pydantic import BaseModel, Field
from typing import List

class WeeklyPlan(BaseModel):
    week: int = Field(description="Số thứ tự của tuần, ví dụ: 1, 2...")
    tasks: List[str] = Field(description="Danh sách các nhiệm vụ học tập trong tuần")

class GoalPlannerResponse(BaseModel):
    weeks: List[WeeklyPlan] = Field(description="Chi tiết lộ trình học chia theo từng tuần")
