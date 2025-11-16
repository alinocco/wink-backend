from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from app.database import Base


class ShotVersion(Base):
    __tablename__ = "shot_versions"

    id = Column(Integer, primary_key=True, index=True)
    shot_id = Column(Integer, ForeignKey("shots.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, index=True)
    
    # Все поля из Shot (копия на момент создания версии)
    order = Column(Integer, nullable=False)
    text = Column(String, nullable=True)
    sketch_image = Column(String, nullable=True)
    middle_image = Column(String, nullable=True)
    final_image = Column(String, nullable=True)
    prompt = Column(String, nullable=True)
    negative_prompt = Column(String, nullable=True)
    params = Column(JSON, nullable=True)
    style = Column(String, nullable=True)
    
    # Метаданные версии
    comment = Column(String, nullable=True)
    is_current = Column(Boolean, default=False, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)

