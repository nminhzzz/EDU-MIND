from pydantic import BaseModel, Field
from typing import List


class TopicScore(BaseModel):
    topic: str = Field(description="Tên chương hoặc chủ đề học tập")
    score: float = Field(
        description="Điểm trung bình hoặc phần trăm nắm vững kiến thức (thang điểm 10)"
    )


class LearningAnalyticsResponse(BaseModel):
    weak_topics: List[TopicScore] = Field(
        description="Danh sách các chủ đề yếu cần cải thiện"
    )
    strong_topics: List[TopicScore] = Field(
        description="Danh sách các chủ đề mạnh học sinh nắm vững"
    )
    learning_trend: str = Field(
        description="Xu hướng học tập, bắt buộc chọn một trong: 'improving' (tiến bộ), 'declining' (sa sút), 'stable' (ổn định)"
    )
    ai_feedback: str = Field(
        description="Đánh giá chi tiết, lời khuyên và nhận xét tổng quan từ AI để giúp học sinh tiến bộ"
    )
