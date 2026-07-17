"""
Script: Trigger lại việc sinh tài liệu (rag_content) cho các plan đã có
nhưng bị thiếu nội dung do lỗi vector search.

Chạy bằng lệnh:
    docker exec backend_dev python scripts/regenerate_rag_content.py --goal_id 29 --student_id <id> --subject_id 18
"""

import argparse
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import configure_logging
from app.database.mysql import SessionLocal
from app.repositories.plan_repository import plan_repository
from app.repositories.subject_repository import subject_repository
from app.services.unified.materials import (
    _generate_and_save_rag_content,
    _is_theory_subject,
    _lecture_system_instruction,
)

configure_logging()

from app.core.logging import get_logger
logger = get_logger(__name__)


async def regenerate_for_goal(goal_id: int, student_id: int, subject_id: int) -> None:
    db = SessionLocal()
    try:
        plans = plan_repository.get_by_goal_and_student(db, goal_id, student_id)
        plans_missing = [p for p in plans if not p.rag_content]
        plans_to_regen = sorted(plans_missing, key=lambda p: p.study_date)[:5]

        subject_obj = subject_repository.get(db, subject_id)
        subject_name = subject_obj.name if subject_obj else ""
        sys_instruction = _lecture_system_instruction(_is_theory_subject(subject_name))

        logger.info(
            "Found %d plans with missing rag_content for goal %d. Regenerating first %d...",
            len(plans_missing),
            goal_id,
            len(plans_to_regen),
        )

        for plan in plans_to_regen:
            logger.info("Processing plan %d: %s", plan.id, plan.title)
            await _generate_and_save_rag_content(db, plan, subject_id, sys_instruction)
            await asyncio.sleep(0.2)

        logger.info("Done. Regenerated %d plans.", len(plans_to_regen))
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal_id", type=int, required=True)
    parser.add_argument("--student_id", type=int, required=True)
    parser.add_argument("--subject_id", type=int, required=True)
    args = parser.parse_args()

    asyncio.run(regenerate_for_goal(args.goal_id, args.student_id, args.subject_id))
