from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.api.schemas.scene import SceneResponse


class ScenarioCreate(BaseModel):
    name: Optional[str] = None
    style: Optional[str] = None


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    style: Optional[str] = None


class ScenarioResponse(BaseModel):
    id: int
    name: Optional[str]
    file_path: str
    params: Optional[Dict[str, Any]] = None
    style: Optional[str] = None
    scenes: List[int] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScenarioExportResponse(BaseModel):
    id: int
    name: Optional[str]
    file_path: str
    params: Optional[Dict[str, Any]] = None
    style: Optional[str] = None
    scenes: List[SceneResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

