from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ShotResponse(BaseModel):
    id: int
    order: int
    text: Optional[str] = None
    image: Optional[str] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    style: Optional[str] = None
    scene_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ShotCreate(BaseModel):
    order: int
    text: Optional[str] = None
    image: Optional[str] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    style: Optional[str] = None


class ShotUpdate(BaseModel):
    order: Optional[int] = None
    text: Optional[str] = None
    image: Optional[str] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    style: Optional[str] = None


class ShotVersionResponse(BaseModel):
    id: int
    shot_id: int
    version_number: int
    order: int
    text: Optional[str] = None
    image: Optional[str] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    style: Optional[str] = None
    comment: Optional[str] = None
    is_current: bool
    created_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class ShotVersionCreate(BaseModel):
    comment: Optional[str] = None


class SceneResponse(BaseModel):
    id: int
    name: str
    scenario_id: int
    params: Optional[Dict[str, Any]] = None
    style: Optional[str] = None
    shots: List[ShotResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

