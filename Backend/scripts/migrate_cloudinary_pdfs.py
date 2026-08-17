"""Migrate legacy raw Cloudinary PDFs to browser-viewable image assets.

The old raw assets are intentionally retained for rollback. Database rows are
updated only after Cloudinary confirms the replacement asset exists.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cloudinary
import cloudinary.api
import cloudinary.uploader

from app.core.config import settings
from app.database.mysql import SessionLocal
from app.models.study_document import StudyDocument


def configure_cloudinary() -> None:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def migrate(*, apply: bool) -> dict[str, object]:
    configure_cloudinary()
    migrated: list[int] = []
    failed: dict[int, str] = {}

    with SessionLocal() as db:
        documents = (
            db.query(StudyDocument)
            .filter(
                StudyDocument.file_type == "pdf",
                StudyDocument.file_path.like("%/raw/upload/%"),
            )
            .order_by(StudyDocument.id)
            .all()
        )
        if not apply:
            return {"candidates": [document.id for document in documents]}

        for document in documents:
            target_id = f"study_documents/document_{document.id}"
            try:
                try:
                    result = cloudinary.api.resource(
                        target_id,
                        resource_type="image",
                        type="authenticated",
                    )
                except Exception:
                    result = cloudinary.uploader.upload(
                        document.file_path,
                        resource_type="image",
                        type="authenticated",
                        public_id=target_id,
                        overwrite=False,
                    )

                secure_url = result.get("secure_url")
                if not secure_url:
                    raise RuntimeError("Cloudinary response did not contain secure_url")

                document.file_path = secure_url
                db.commit()
                migrated.append(document.id)
            except Exception as exc:
                db.rollback()
                failed[document.id] = str(exc)

    return {"migrated": migrated, "failed": failed}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(migrate(apply=args.apply))
