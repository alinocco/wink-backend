from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class Shot(Base):
    __tablename__ = "shots"

    id = Column(Integer, primary_key=True, index=True)
    order = Column(Integer, nullable=False, index=True)
    text = Column(String, nullable=True)
    image = Column(String, nullable=True)  # Path to locally saved image
    prompt = Column(String, nullable=True)
    negative_prompt = Column(String, nullable=True)
    params = Column(JSON, nullable=True)
    style = Column(String, nullable=True)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=False, index=True)
    current_version_id = Column(Integer, ForeignKey("shot_versions.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

