from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.database import get_db
from app.models.scenario import Scenario
from app.models.scene import Scene
from app.models.shot import Shot
from app.models.shot_version import ShotVersion
from app.api.schemas.scene import ShotResponse, ShotCreate, ShotUpdate, ShotVersionResponse, ShotVersionCreate

router = APIRouter(prefix="/scenarios/{scenario_id}/scenes/{scene_id}/shots", tags=["shots"])


async def verify_scene_belongs_to_scenario(
    scenario_id: int,
    scene_id: int,
    db: AsyncSession
) -> Scene:
    """Проверяет существование сценария и сцены, и их связь"""
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
    
    return scene


@router.get("/", response_model=List[ShotResponse])
async def get_shots(
    scenario_id: int,
    scene_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех shots для сцены"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Загружаем shots для этой сцены, отсортированные по order
    shots_result = await db.execute(
        select(Shot).filter(Shot.scene_id == scene_id).order_by(Shot.order)
    )
    shots = shots_result.scalars().all()
    return list(shots)


@router.get("/{shot_id}", response_model=ShotResponse)
async def get_shot(
    scenario_id: int,
    scene_id: int,
    shot_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить конкретный shot"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Проверяем существование shot и его принадлежность к сцене
    shot_result = await db.execute(
        select(Shot).filter(
            Shot.id == shot_id,
            Shot.scene_id == scene_id
        )
    )
    shot = shot_result.scalar_one_or_none()
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shot not found"
        )
    
    return shot


@router.post("/", response_model=ShotResponse, status_code=status.HTTP_201_CREATED)
async def create_shot(
    scenario_id: int,
    scene_id: int,
    shot_create: ShotCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новый shot"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Создаем новый shot
    db_shot = Shot(
        order=shot_create.order,
        text=shot_create.text,
        prompt=shot_create.prompt,
        negative_prompt=shot_create.negative_prompt,
        params=shot_create.params,
        style=shot_create.style,
        scene_id=scene_id
    )
    db.add(db_shot)
    await db.commit()
    await db.refresh(db_shot)
    
    # Создаем первую версию
    version = ShotVersion(
        shot_id=db_shot.id,
        version_number=1,
        order=db_shot.order,
        text=db_shot.text,
        prompt=db_shot.prompt,
        negative_prompt=db_shot.negative_prompt,
        params=db_shot.params,
        style=db_shot.style,
        is_current=True
    )
    db.add(version)
    await db.commit()
    await db.refresh(version)
    
    # Устанавливаем текущую версию
    db_shot.current_version_id = version.id
    await db.commit()
    await db.refresh(db_shot)
    
    return db_shot


@router.put("/{shot_id}", response_model=ShotResponse)
async def update_shot(
    scenario_id: int,
    scene_id: int,
    shot_id: int,
    shot_update: ShotUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить shot"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Проверяем существование shot и его принадлежность к сцене
    shot_result = await db.execute(
        select(Shot).filter(
            Shot.id == shot_id,
            Shot.scene_id == scene_id
        )
    )
    shot = shot_result.scalar_one_or_none()
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shot not found"
        )
    
    # Сохраняем старые значения для создания версии
    old_order = shot.order
    old_text = shot.text
    old_prompt = shot.prompt
    old_negative_prompt = shot.negative_prompt
    old_params = shot.params
    
    # Обновляем поля
    has_changes = False
    if shot_update.order is not None and shot_update.order != shot.order:
        shot.order = shot_update.order
        has_changes = True
    if shot_update.text is not None and shot_update.text != shot.text:
        shot.text = shot_update.text
        has_changes = True
    if shot_update.prompt is not None and shot_update.prompt != shot.prompt:
        shot.prompt = shot_update.prompt
        has_changes = True
    if shot_update.negative_prompt is not None and shot_update.negative_prompt != shot.negative_prompt:
        shot.negative_prompt = shot_update.negative_prompt
        has_changes = True
    if shot_update.params is not None and shot_update.params != shot.params:
        shot.params = shot_update.params
        has_changes = True
    if shot_update.style is not None and shot_update.style != shot.style:
        shot.style = shot_update.style
        has_changes = True
    
    # Если есть изменения, создаем новую версию
    if has_changes:
        # Получаем следующий номер версии
        max_version_result = await db.execute(
            select(func.max(ShotVersion.version_number)).filter(ShotVersion.shot_id == shot_id)
        )
        max_version = max_version_result.scalar_one_or_none() or 0
        next_version = max_version + 1
        
        # Снимаем флаг is_current со всех предыдущих версий
        current_versions_result = await db.execute(
            select(ShotVersion).filter(
                ShotVersion.shot_id == shot_id,
                ShotVersion.is_current == True
            )
        )
        for v in current_versions_result.scalars().all():
            v.is_current = False
        
        # Создаем новую версию с новыми значениями
        new_version = ShotVersion(
            shot_id=shot_id,
            version_number=next_version,
            order=shot.order,
            text=shot.text,
            prompt=shot.prompt,
            negative_prompt=shot.negative_prompt,
            params=shot.params,
            style=shot.style,
            is_current=True
        )
        db.add(new_version)
        await db.commit()
        await db.refresh(new_version)
        
        # Устанавливаем текущую версию
        shot.current_version_id = new_version.id
    
    await db.commit()
    await db.refresh(shot)
    return shot


@router.delete("/{shot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shot(
    scenario_id: int,
    scene_id: int,
    shot_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить shot"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Проверяем существование shot и его принадлежность к сцене
    shot_result = await db.execute(
        select(Shot).filter(
            Shot.id == shot_id,
            Shot.scene_id == scene_id
        )
    )
    shot = shot_result.scalar_one_or_none()
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shot not found"
        )
    
    # Удаляем shot
    await db.delete(shot)
    await db.commit()
    return None


@router.post("/{shot_id}/action/final", response_model=ShotResponse)
async def finalize_shot(
    scenario_id: int,
    scene_id: int,
    shot_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Финализировать shot (заглушка)"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Проверяем существование shot и его принадлежность к сцене
    shot_result = await db.execute(
        select(Shot).filter(
            Shot.id == shot_id,
            Shot.scene_id == scene_id
        )
    )
    shot = shot_result.scalar_one_or_none()
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shot not found"
        )
    
    # TODO: Реализовать логику финализации shot
    # Заглушка - просто возвращаем shot без изменений
    return shot


@router.post("/{shot_id}/action/regenerate", response_model=ShotResponse)
async def regenerate_shot(
    scenario_id: int,
    scene_id: int,
    shot_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Регенерировать shot (заглушка)"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Проверяем существование shot и его принадлежность к сцене
    shot_result = await db.execute(
        select(Shot).filter(
            Shot.id == shot_id,
            Shot.scene_id == scene_id
        )
    )
    shot = shot_result.scalar_one_or_none()
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shot not found"
        )
    
    # TODO: Реализовать логику регенерации shot
    # Заглушка - просто возвращаем shot без изменений
    return shot


# Эндпоинты для работы с версиями
@router.get("/{shot_id}/versions", response_model=List[ShotVersionResponse])
async def get_shot_versions(
    scenario_id: int,
    scene_id: int,
    shot_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех версий shot"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Проверяем существование shot и его принадлежность к сцене
    shot_result = await db.execute(
        select(Shot).filter(
            Shot.id == shot_id,
            Shot.scene_id == scene_id
        )
    )
    shot = shot_result.scalar_one_or_none()
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shot not found"
        )
    
    # Загружаем все версии, отсортированные по номеру версии (по убыванию)
    versions_result = await db.execute(
        select(ShotVersion).filter(ShotVersion.shot_id == shot_id).order_by(ShotVersion.version_number.desc())
    )
    versions = versions_result.scalars().all()
    return list(versions)


@router.get("/{shot_id}/versions/{version_id}", response_model=ShotVersionResponse)
async def get_shot_version(
    scenario_id: int,
    scene_id: int,
    shot_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить конкретную версию shot"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Проверяем существование shot и его принадлежность к сцене
    shot_result = await db.execute(
        select(Shot).filter(
            Shot.id == shot_id,
            Shot.scene_id == scene_id
        )
    )
    shot = shot_result.scalar_one_or_none()
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shot not found"
        )
    
    # Проверяем существование версии и её принадлежность к shot
    version_result = await db.execute(
        select(ShotVersion).filter(
            ShotVersion.id == version_id,
            ShotVersion.shot_id == shot_id
        )
    )
    version = version_result.scalar_one_or_none()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return version


@router.post("/{shot_id}/versions", response_model=ShotVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_shot_version(
    scenario_id: int,
    scene_id: int,
    shot_id: int,
    version_create: ShotVersionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новую версию shot из текущего состояния"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Проверяем существование shot и его принадлежность к сцене
    shot_result = await db.execute(
        select(Shot).filter(
            Shot.id == shot_id,
            Shot.scene_id == scene_id
        )
    )
    shot = shot_result.scalar_one_or_none()
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shot not found"
        )
    
    # Получаем следующий номер версии
    max_version_result = await db.execute(
        select(func.max(ShotVersion.version_number)).filter(ShotVersion.shot_id == shot_id)
    )
    max_version = max_version_result.scalar_one_or_none() or 0
    next_version = max_version + 1
    
    # Снимаем флаг is_current со всех предыдущих версий
    current_versions_result = await db.execute(
        select(ShotVersion).filter(
            ShotVersion.shot_id == shot_id,
            ShotVersion.is_current == True
        )
    )
    for v in current_versions_result.scalars().all():
        v.is_current = False
    
    # Создаем новую версию из текущего состояния shot
    new_version = ShotVersion(
        shot_id=shot_id,
        version_number=next_version,
        order=shot.order,
        text=shot.text,
        prompt=shot.prompt,
        negative_prompt=shot.negative_prompt,
        params=shot.params,
        style=shot.style,
        comment=version_create.comment,
        is_current=True
    )
    db.add(new_version)
    await db.commit()
    await db.refresh(new_version)
    
    # Устанавливаем текущую версию
    shot.current_version_id = new_version.id
    await db.commit()
    
    return new_version


@router.put("/{shot_id}/versions/{version_id}/set-current", response_model=ShotResponse)
async def set_current_version(
    scenario_id: int,
    scene_id: int,
    shot_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Установить конкретную версию как текущую и восстановить её значения в shot"""
    await verify_scene_belongs_to_scenario(scenario_id, scene_id, db)
    
    # Проверяем существование shot и его принадлежность к сцене
    shot_result = await db.execute(
        select(Shot).filter(
            Shot.id == shot_id,
            Shot.scene_id == scene_id
        )
    )
    shot = shot_result.scalar_one_or_none()
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shot not found"
        )
    
    # Проверяем существование версии и её принадлежность к shot
    version_result = await db.execute(
        select(ShotVersion).filter(
            ShotVersion.id == version_id,
            ShotVersion.shot_id == shot_id
        )
    )
    version = version_result.scalar_one_or_none()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    # Снимаем флаг is_current со всех версий
    current_versions_result = await db.execute(
        select(ShotVersion).filter(
            ShotVersion.shot_id == shot_id,
            ShotVersion.is_current == True
        )
    )
    for v in current_versions_result.scalars().all():
        v.is_current = False
    
    # Устанавливаем выбранную версию как текущую
    version.is_current = True
    
    # Восстанавливаем значения из версии в shot
    shot.order = version.order
    shot.text = version.text
    shot.prompt = version.prompt
    shot.negative_prompt = version.negative_prompt
    shot.params = version.params
    shot.style = version.style
    shot.current_version_id = version.id
    
    await db.commit()
    await db.refresh(shot)
    return shot

