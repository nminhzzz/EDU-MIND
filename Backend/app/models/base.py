from app.database.mysql import Base

# Gom Base của SQLAlchemy từ database layer về đây để làm điểm import chung cho models
__all__ = ["Base"]
