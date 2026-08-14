import unittest
from unittest.mock import Mock

from app.models.outbox_job import OutboxJob
from app.services.outbox_service import stage_outbox_job


class OutboxStagingTests(unittest.TestCase):
    def test_job_is_staged_without_committing(self):
        db = Mock()

        job = stage_outbox_job(
            db,
            task_name="app.workers.tasks.task_index_study_document",
            args=[42],
            unique_key="document-index:42",
        )

        self.assertIsInstance(job, OutboxJob)
        self.assertEqual(job.payload, {"args": [42], "kwargs": {}})
        db.add.assert_called_once_with(job)
        db.commit.assert_not_called()

    def test_unknown_task_is_rejected(self):
        db = Mock()

        with self.assertRaises(ValueError):
            stage_outbox_job(
                db,
                task_name="untrusted.task",
                args=[],
                unique_key="bad:1",
            )

        db.add.assert_not_called()


if __name__ == "__main__":
    unittest.main()
