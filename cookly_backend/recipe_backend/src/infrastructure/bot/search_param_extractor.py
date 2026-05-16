import json
import logging

import aiohttp
from starlette import status

from core.config import OllamaConfig
from domain.entities.value_objects import MealTimeType
from presentation.web_api.routes.recipe.schemas import SearchRecipeQuery

INGREDIENT_GROUPS = {
    1: "Животное происхождение",
    2: "Овощи",
    3: "Фрукты",
    4: "Ягоды",
    5: "Зелень",
    6: "Мясо",
    7: "Птица",
    8: "Рыба и морепродукты",
    9: "Молочные продукты",
    10: "Яйца",
    11: "Зерновые и крупы",
    12: "Бобовые",
    13: "Орехи и семена",
    14: "Сладости",
    15: "Выпечка и мука",
    16: "Соусы и приправы",
    17: "Специи",
    18: "Масла и жиры",
    19: "Консервы",
    20: "Полуфабрикаты",
    21: "Глютен",
    22: "Лактоза",
    23: "Сахар",
    24: "Вегетарианские",
    25: "Веганские"
}
MEAL_TIMES = {
    "breakfast": "завтрак",
    "lunch": "обед",
    "supper": "ужин",
}
SYSTEM_PROMPT = (
    "Ты — парсер запросов для поиска рецептов. "
    "Из ЛЮБОГО запроса про еду, рецепты, готовку извлеки параметры.\n\n"
    "Верни ТОЛЬКО JSON, БЕЗ текста вне JSON.\n\n"
    f"Группы ингредиентов: {json.dumps(INGREDIENT_GROUPS, ensure_ascii=False)}\n"
    f"Приёмы пищи: {json.dumps(MEAL_TIMES, ensure_ascii=False)}\n\n"
    "ПРАВИЛА:\n"
    '1. Ответ — ТОЛЬКО JSON: {"query": "..."} или [{...}]\n'
    "2. НЕ пиши текст ДО или ПОСЛЕ JSON.\n"
    '3. not_food_related ТОЛЬКО если запрос СОВСЕМ не про еду (погода, политика, "как дела?", математика).\n'
    '   Если запрос упоминает еду, ингредиенты, блюда, готовку, приём пищи — это про еду!\n'
    "4. МЕНЮ (слова «меню», «на день», «рацион», «план питания») → МАССИВ\n"
    "5. ОДИН запрос → ОДИН объект\n\n"
    "6. Повторять в 'query' то что отразил в других параметрах - не надо, то есть если добавил "
    '"exclude_ingredient_group_ids": [21], то в query о глютене повторять не надо\n'
    "ПОЛЯ (только эти):\n"
    "- query (ОБЯЗАТЕЛЬНО) — ключевые слова + синонимы, макс 10 слов:\n"
    "  холодное → «салат окрошка холодный»\n"
    "  быстрое → «быстрый» + max_estimated_cooking_time=30\n"
    "  сладкое → «десерт торт пирог»\n"
    "  сытное → «мясо запеканка паста»\n"
    " в том чиcле meal_time_type и несколько ключевых слов -"
    " например для ужина: мясо, курица, макароны, тушеный, жарен\n "
    "- include_ingredient_group_ids: [int]\n"
    "- exclude_ingredient_group_ids: [int]\n"
    "- max_spicy: 0-5\n"
    "- max_difficulty: 1-5\n"
    "- max_calories_by_100grams: float\n"
    "- max_estimated_cooking_time: int (минуты)\n"
    '- meal_time_type: "breakfast"|"lunch"|"supper"\n'
    # "- min_avg_rating: 0-5\n"
    "- limit: меню=3, поиск=4\n\n"
    "ПРИМЕРЫ:\n"
    '«хочу холодненького» → {"query": "холодный салат окрошка закуска", "limit": 4}\n'
    '«быстрый ужин без лактозы» → {"query": "быстрый ужин", "meal_time_type": "supper", '
    '"exclude_ingredient_group_ids": [22], "max_estimated_cooking_time": 30, "limit": 3}\n'
    '«хочу есть» → {"query": "быстрый блюдо рецепт", "limit": 5, "max_estimated_cooking_time": 30}\n'
    '«как дела?» → {"error": "not_food_related"}\n'
    '«2+2» → {"error": "not_food_related"}'
)
logger = logging.getLogger(__name__)


class OllamaRecipeExtractor:
    def __init__(
        self,
        config: OllamaConfig
    ):
        self.url = config.url
        self.model = config.model
        self.timeout = config.timeout

    async def extract_search_params(
        self,
        user_message: str
    ) -> list[dict] | dict | str | None:
        url = f"{self.url}/api/chat"
        payload = self._build_payload(user_message)

        try:
            content = await self._send_request(url, payload)
            if content is None:
                return None

            parsed = self._parse_response(content)
            return self._validate_response(parsed)
        except Exception as e:
            logger.exception("Unexpected error: %s", e)
            return None

    def _build_payload(self, user_message: str) -> dict:
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
            }
        }

    async def _send_request(self, url: str, payload: dict) -> str | None:
        try:
            async with aiohttp.ClientSession() as session, session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != status.HTTP_200_OK:
                    logger.exception("Ollama error: %s", response.status)
                    return None

                result = await response.json()
                content = result["message"]["content"].strip()
                return self._clean_content(content)
        except Exception as e:
            logger.exception("Request failed: %s", exc_info=e)
            return None

    def _clean_content(self, content: str) -> str:
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:])
            if content.endswith("```"):
                content = content[:-3]
        return content.strip()

    def _parse_response(self, content: str) -> dict | list | None:
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            parsed = self._extract_json_objects(content)
            if parsed is None:
                logger.exception("Failed to parse Ollama response: %s", content, exc_info=e)
            return parsed

    def _validate_response(self, parsed: dict | list | None) -> list[dict] | dict | str | None:
        if parsed is None:
            return None

        if isinstance(parsed, dict):
            if "error" in parsed:
                return parsed["error"]
            return parsed

        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict) and "error" in item:
                    return "not_food_related"
            return parsed

        return None

    def _extract_json_objects(self, text: str) -> dict | list | None:
        text = text.strip()
        results = []
        depth = 0
        start_idx = None

        open_chars = {"{", "["}
        close_chars = {"}", "]"}

        for i, char in enumerate(text):
            if char in open_chars:
                if depth == 0:
                    start_idx = i
                depth += 1
            elif char in close_chars:
                depth -= 1
                if depth == 0 and start_idx is not None:
                    try:
                        obj = json.loads(text[start_idx:i + 1])
                        results.append(obj)
                    except json.JSONDecodeError:
                        pass
                    start_idx = None

        return self._handle_results(results)

    def _handle_results(self, results: list) -> dict | list | None:
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]
        else:
            return results

    def params_to_query(self, params: dict) -> SearchRecipeQuery:
        logger.info("User params: %s", params)
        if mtt := params.get("meal_time_type"):
            if isinstance(mtt, str):
                mtts = mtt.split()
                if  len(mtts) > 1:
                    params["meal_time_type"] = [MealTimeType(m) for m in mtts]
                else:
                    params["meal_time_type"] = MealTimeType(mtt)
            elif isinstance(mtt, list):
                params["meal_time_type"] = [MealTimeType(m) for m in mtt]
        if not params.get("limit"):
            params["limit"] = 3

        return SearchRecipeQuery(**params)
