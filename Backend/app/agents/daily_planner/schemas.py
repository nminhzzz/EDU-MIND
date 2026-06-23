from pydantic import BaseModel, Field
from typing import List

class DailyScheduleTask(BaseModel):
    date: str = Field(description="Ngày học định dạng YYYY-MM-DD")
    start_time: str = Field(description="Giờ bắt đầu định dạng HH:MM")
    end_time: str = Field(description="Giờ kết thúc định dạng HH:MM")
    task: str = Field(description="Nhiệm vụ học tập cụ thể")
    description: str = Field(description="Mô tả chi tiết nội dung học tập hoặc nhiệm vụ cần hoàn thành")

class DailyPlannerResponse(BaseModel):
    schedule: List[DailyScheduleTask] = Field(description="Thời khóa biểu chi tiết hàng ngày")
