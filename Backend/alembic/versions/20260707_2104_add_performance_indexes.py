"""add_performance_indexes

Revision ID: add_perf_indexes_001
Revises: 39614d5fd32b
Create Date: 2026-07-07 21:04:00

Adds composite indexes on high-traffic query paths to eliminate full-table scans:
  - study_plans(student_id, study_date) — dashboard & scheduler queries
  - study_plans(goal_id)               — goal→plan join
  - quiz_attempts(student_id, quiz_id) — analytics recalc queries
  - learning_analytics(student_id, subject_id) + UNIQUE constraint
  - notifications(user_id, is_read)    — unread count queries
  - quizzes(student_id, subject_id)    — quiz list by student/subject
"""

from alembic import op

# revision identifiers
revision = "add_perf_indexes_001"
down_revision = "39614d5fd32b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # study_plans
    op.create_index(
        "ix_study_plan_student_date",
        "study_plans",
        ["student_id", "study_date"],
        unique=False,
    )
    op.create_index(
        "ix_study_plan_goal",
        "study_plans",
        ["goal_id"],
        unique=False,
    )

    # quiz_attempts
    op.create_index(
        "ix_quiz_attempt_student_quiz",
        "quiz_attempts",
        ["student_id", "quiz_id"],
        unique=False,
    )

    # learning_analytics — unique on (student_id, subject_id)
    op.create_index(
        "ix_learning_analytic_student_subject",
        "learning_analytics",
        ["student_id", "subject_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_analytic_student_subject",
        "learning_analytics",
        ["student_id", "subject_id"],
    )

    # notifications
    op.create_index(
        "ix_notification_user_read",
        "notifications",
        ["user_id", "is_read"],
        unique=False,
    )

    # quizzes
    op.create_index(
        "ix_quiz_student_subject",
        "quizzes",
        ["student_id", "subject_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_quiz_student_subject", table_name="quizzes")
    op.drop_index("ix_notification_user_read", table_name="notifications")
    op.drop_constraint(
        "uq_analytic_student_subject", "learning_analytics", type_="unique"
    )
    op.drop_index(
        "ix_learning_analytic_student_subject", table_name="learning_analytics"
    )
    op.drop_index("ix_quiz_attempt_student_quiz", table_name="quiz_attempts")
    op.drop_index("ix_study_plan_goal", table_name="study_plans")
    op.drop_index("ix_study_plan_student_date", table_name="study_plans")
