from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pathlib import Path
import os
import uuid
from enum import Enum
from app.database import get_db
from app.models.scenario import Scenario
from app.models.scene import Scene
from app.models.shot import Shot
from app.api.schemas.scenario import ScenarioCreate, ScenarioUpdate, ScenarioResponse, ScenarioExportResponse
from app.api.schemas.scene import SceneResponse, ShotResponse

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

# Директория для хранения PDF файлов
UPLOAD_DIR = Path("uploads/scenarios")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class ExportDataType(str, Enum):
    JSON = "json"
    # Можно добавить другие форматы в будущем, например PDF, XML и т.д.


@router.post("/", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    style: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    # Проверка типа файла
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Генерируем уникальное имя файла
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Если имя не указано, используем имя файла (без расширения)
    if not name:
        name = Path(file.filename).stem
    
    # Сохраняем файл локально
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Создаем запись в БД
    db_scenario = Scenario(
        name=name,
        file_path=str(file_path),
        style=style
    )
    db.add(db_scenario)
    await db.commit()
    await db.refresh(db_scenario)
    
    # Возвращаем сценарий с пустым массивом сцен
    return ScenarioResponse(
        id=db_scenario.id,
        name=db_scenario.name,
        file_path=db_scenario.file_path,
        params=db_scenario.params,
        style=db_scenario.style,
        scenes=[],
        created_at=db_scenario.created_at,
        updated_at=db_scenario.updated_at
    )


@router.get("/", response_model=List[ScenarioResponse])
async def get_scenarios(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Scenario).offset(skip).limit(limit))
    scenarios = result.scalars().all()
    
    if not scenarios:
        return []
    
    # Загружаем все сцены для всех сценариев одним запросом
    scenario_ids = [s.id for s in scenarios]
    scenes_result = await db.execute(
        select(Scene).filter(Scene.scenario_id.in_(scenario_ids))
    )
    scenes = scenes_result.scalars().all()
    
    # Группируем сцены по scenario_id
    scenes_by_scenario = {}
    for scene in scenes:
        if scene.scenario_id not in scenes_by_scenario:
            scenes_by_scenario[scene.scenario_id] = []
        scenes_by_scenario[scene.scenario_id].append(scene.id)
    
    # Формируем ответ с scenes для каждого сценария
    return [
        ScenarioResponse(
            id=scenario.id,
            name=scenario.name,
            file_path=scenario.file_path,
            params=scenario.params,
            style=scenario.style,
            scenes=scenes_by_scenario.get(scenario.id, []),
            created_at=scenario.created_at,
            updated_at=scenario.updated_at
        )
        for scenario in scenarios
    ]


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Scenario).filter(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    # Загружаем сцены для этого сценария
    scenes_result = await db.execute(
        select(Scene).filter(Scene.scenario_id == scenario_id)
    )
    scenes = scenes_result.scalars().all()
    scene_ids = [scene.id for scene in scenes]
    
    return ScenarioResponse(
        id=scenario.id,
        name=scenario.name,
        file_path=scenario.file_path,
        params=scenario.params,
        style=scenario.style,
        scenes=scene_ids,
        created_at=scenario.created_at,
        updated_at=scenario.updated_at
    )


@router.get("/{scenario_id}/scenes/{scene_id}", response_model=SceneResponse)
async def get_scene(
    scenario_id: int,
    scene_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Проверяем существование сценария
    scenario_result = await db.execute(select(Scenario).filter(Scenario.id == scenario_id))
    scenario = scenario_result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    # Проверяем существование сцены и её принадлежность к сценарию
    scene_result = await db.execute(
        select(Scene).filter(
            Scene.id == scene_id,
            Scene.scenario_id == scenario_id
        )
    )
    scene = scene_result.scalar_one_or_none()
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    # Загружаем shots для этой сцены, отсортированные по order
    shots_result = await db.execute(
        select(Shot).filter(Shot.scene_id == scene_id).order_by(Shot.order)
    )
    shots = shots_result.scalars().all()
    
    # Создаем ответ с shots
    return SceneResponse(
        id=scene.id,
        name=scene.name,
        scenario_id=scene.scenario_id,
        params=scene.params,
        style=scene.style,
        shots=list(shots),
        created_at=scene.created_at,
        updated_at=scene.updated_at
    )


@router.get("/{scenario_id}/download")
async def download_scenario_file(
    scenario_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Scenario).filter(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    if not scenario.file_path or not os.path.exists(scenario.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=scenario.file_path,
        media_type="application/pdf",
        filename=scenario.name + ".pdf" if scenario.name else f"scenario_{scenario_id}.pdf"
    )


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: int,
    scenario_update: ScenarioUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Scenario).filter(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    # Обновляем поля
    if scenario_update.name is not None:
        scenario.name = scenario_update.name
    if scenario_update.style is not None:
        scenario.style = scenario_update.style
    
    await db.commit()
    await db.refresh(scenario)
    
    # Загружаем сцены для этого сценария
    scenes_result = await db.execute(
        select(Scene).filter(Scene.scenario_id == scenario_id)
    )
    scenes = scenes_result.scalars().all()
    scene_ids = [scene.id for scene in scenes]
    
    return ScenarioResponse(
        id=scenario.id,
        name=scenario.name,
        file_path=scenario.file_path,
        params=scenario.params,
        style=scenario.style,
        scenes=scene_ids,
        created_at=scenario.created_at,
        updated_at=scenario.updated_at
    )


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Scenario).filter(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    # Удаляем файл с диска
    if scenario.file_path and os.path.exists(scenario.file_path):
        try:
            os.remove(scenario.file_path)
        except Exception as e:
            # Логируем ошибку, но продолжаем удаление записи из БД
            print(f"Failed to delete file {scenario.file_path}: {str(e)}")
    
    # Удаляем запись из БД
    await db.delete(scenario)
    await db.commit()
    return None


@router.post("/{scenario_id}/action/export", response_model=ScenarioExportResponse)
async def export_scenario(
    scenario_id: int,
    data_type: ExportDataType = Query(ExportDataType.JSON, description="Тип данных для экспорта"),
    db: AsyncSession = Depends(get_db)
):
    """
    Экспортировать сценарий со всеми сценами и shots
    """
    # Проверяем существование сценария
    result = await db.execute(select(Scenario).filter(Scenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    # Загружаем все сцены для этого сценария
    scenes_result = await db.execute(
        select(Scene).filter(Scene.scenario_id == scenario_id).order_by(Scene.id)
    )
    scenes = scenes_result.scalars().all()
    
    # Для каждой сцены загружаем shots
    scene_responses = []
    for scene in scenes:
        shots_result = await db.execute(
            select(Shot).filter(Shot.scene_id == scene.id).order_by(Shot.order)
        )
        shots = shots_result.scalars().all()
        
        shot_responses = [
            ShotResponse(
                id=shot.id,
                order=shot.order,
                text=shot.text,
                image=shot.image,
                prompt=shot.prompt,
                negative_prompt=shot.negative_prompt,
                params=shot.params,
                style=shot.style,
                scene_id=shot.scene_id,
                created_at=shot.created_at,
                updated_at=shot.updated_at
            )
            for shot in shots
        ]
        
        scene_responses.append(
            SceneResponse(
                id=scene.id,
                name=scene.name,
                scenario_id=scene.scenario_id,
                params=scene.params,
                style=scene.style,
                shots=shot_responses,
                created_at=scene.created_at,
                updated_at=scene.updated_at
            )
        )
    
    # Формируем ответ с полными данными
    export_response = ScenarioExportResponse(
        id=scenario.id,
        name=scenario.name,
        file_path=scenario.file_path,
        params=scenario.params,
        style=scenario.style,
        scenes=scene_responses,
        created_at=scenario.created_at,
        updated_at=scenario.updated_at
    )
    
    # В зависимости от типа данных возвращаем соответствующий ответ
    if data_type == ExportDataType.JSON:
        return export_response
    else:
        # Для других форматов можно добавить дополнительную логику
        return export_response

