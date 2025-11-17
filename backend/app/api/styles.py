from fastapi import APIRouter
from app.api.schemas.style import StylesResponse, StyleOption

router = APIRouter(prefix="/styles", tags=["styles"])

# Захардкоженные варианты стилей
HARDCODED_STYLES = [
    StyleOption(
        id="cinematic",
        name="Cinematic",
        description="Кинематографический стиль с глубокими тенями и драматичным освещением"
    ),
    StyleOption(
        id="realistic",
        name="Realistic",
        description="Реалистичный стиль с естественным освещением и детализацией"
    ),
    StyleOption(
        id="anime",
        name="Anime",
        description="Аниме стиль с яркими цветами и выразительными персонажами"
    ),
    StyleOption(
        id="cartoon",
        name="Cartoon",
        description="Мультяшный стиль с упрощенными формами и яркими цветами"
    ),
    StyleOption(
        id="noir",
        name="Film Noir",
        description="Стиль нуар с контрастным черно-белым изображением"
    ),
    StyleOption(
        id="fantasy",
        name="Fantasy",
        description="Фэнтези стиль с магическими элементами и необычным освещением"
    ),
    StyleOption(
        id="sci-fi",
        name="Sci-Fi",
        description="Научно-фантастический стиль с футуристическими элементами"
    ),
    StyleOption(
        id="vintage",
        name="Vintage",
        description="Винтажный стиль с ретро-эстетикой и приглушенными цветами"
    ),
]


@router.get("/", response_model=StylesResponse)
async def get_styles():
    """
    Получить список доступных стилей
    """
    return StylesResponse(styles=HARDCODED_STYLES)

