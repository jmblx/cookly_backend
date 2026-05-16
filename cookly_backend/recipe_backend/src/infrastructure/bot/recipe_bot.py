import asyncio
import re
import time

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from application.recipe.common.service import RecipeService
from core.config import OllamaConfig
from infrastructure.bot.search_param_extractor import MEAL_TIMES, OllamaRecipeExtractor, logger


class RecipeBot:
    def __init__(
        self,
        recipe_service: RecipeService,
        ollama_config: OllamaConfig,
        extractor: OllamaRecipeExtractor,
        session: AsyncSession
    ):
        self.recipe_service = recipe_service
        self.ollama_url = ollama_config.url
        self.extractor = extractor
        self.session = session
        self.ALLOWED_ENGLISH_WORDS_LENGTH = 2

    async def process_message(
        self,
        user_message: str,
    ) -> dict:
        import time
        time_start = time.time()
        params = await self.extractor.extract_search_params(user_message)
        logger.info(f"Extract params time: {time.time() - time_start}")

        if params is None:
            return {
                "is_food_related": False,
                "text_response": "Извините, произошла ошибка при обработке запроса.",
                "recipes": [],
            }

        if params == "not_food_related":
            refusal = await self._generate_refusal(user_message)
            logger.info(f"Refusal time: {time.time() - time_start}")
            return {
                "is_food_related": False,
                "text_response": refusal,
                "recipes": [],
            }

        if isinstance(params, list):
            search_params_list = params
        else:
            search_params_list = [params]

        all_recipes = []
        search_queries_info = []

        for search_params_dict in search_params_list:
            search_params = self.extractor.params_to_query(search_params_dict)
            logger.info(f"Search params time: {time.time() - time_start}")

            recipes = await self.recipe_service.search_recipes(
                query_data=search_params,
            )
            logger.info(f"Search time: {time.time() - time_start}")

            if recipes:
                all_recipes.extend(recipes)
                search_queries_info.append({
                    "query": search_params_dict.get("query", ""),
                    "meal_time": search_params_dict.get("meal_time_type", ""),
                    "recipes": recipes,
                    "count": len(recipes)
                })

        unique_recipes = []
        seen_ids = set()
        for recipe in all_recipes:
            if recipe.id not in seen_ids:
                unique_recipes.append(recipe)
                seen_ids.add(recipe.id)

        if unique_recipes:
            recipe_ids = [r.id for r in unique_recipes]
            ingredients_map = await self.recipe_service.load_recipes_ingredients(recipe_ids)
        else:
            ingredients_map = {}

        if unique_recipes:
            logger.info(f"Generate response time: {time.time() - time_start}")
            text_response = await self._generate_recipe_response(
                user_message=user_message,
                search_queries_info=search_queries_info,
                recipes=unique_recipes,
                ingredients_map=ingredients_map
            )
            logger.info(f"Generated response time: {time.time() - time_start}")

        else:
            logger.info(f"Generate no results response time: {time.time() - time_start}")
            text_response = await self._generate_no_results_response(
                user_message=user_message,
            )
            logger.info(f"Generated no results response time: {time.time() - time_start}")

        return {
            "is_food_related": True,
            "text_response": text_response,
            "recipes": unique_recipes,
        }

    async def _generate_recipe_response(
        self,
        user_message: str,
        search_queries_info: list[dict],
        recipes: list,
        ingredients_map: dict[int, list[str]]
    ) -> str:
        """Генерирует текстовый ответ с рекомендациями рецептов"""
        has_multiple_queries = len(search_queries_info) > 1

        if has_multiple_queries:
            # Меню на день
            context_parts = []
            for sq in search_queries_info:
                meal_key = sq.get("meal_time", "")
                meal_name = MEAL_TIMES.get(meal_key, meal_key or "блюдо")
                context_parts.append(f"Для {meal_name}:")
                for recipe in sq["recipes"][:1]:
                    ingredients = ingredients_map.get(recipe.id, [])
                    ingr_text = ", ".join(ingredients[:8])

                    context_parts.append(
                        f"— {recipe.title}: {recipe.description or ''} "
                        f"(~{recipe.calories_by_100grams} ккал/100г, "
                        f"около {recipe.estimated_time or '?'} мин)"
                        f"\n  Ингредиенты: {ingr_text}"
                    )
            recipes_context = "\n".join(context_parts)

            instruction = (
                "Представь это как меню, по одному блюду на каждый приём пищи. "
                "Для каждого кратко скажи, почему оно подходит."
            )
        else:
            context_parts = []
            for i, recipe in enumerate(recipes[:5], 1):
                ingredients = ingredients_map.get(recipe.id, [])
                ingr_text = ", ".join(ingredients[:10])

                context_parts.append(
                    f"{i}. {recipe.title}: {recipe.description or ''} "
                    f"(~{recipe.calories_by_100grams} ккал/100г, "
                    f"около {recipe.estimated_time or '?'} мин)"
                    f"\n   Ингредиенты: {ingr_text}"
                )
            recipes_context = "\n".join(context_parts)

            instruction = (
        "Если хоть частичного совпадения по критериям по твоей оценке нет — скажи, что однозначно "
        "подходящего рецепта не найдено и мягко очень коротко предложи переформулировать и/или уточнить запрос. "
        "если совпадение есть, то выбери 1-2 наиболее подходящих рецепта и расскажи о них кратко, "
        "неявно подводя под запрос пользователя."
        "Не описывай приготовление в деталях и не расписывай конкретные шаги и ингредиенты. "
    )

        prompt = f"""{instruction}

    Запрос пользователя: "{user_message}"

    Среди рецептов найдены:
    {recipes_context}

    ПРАВИЛА ОТВЕТА:
    - Только русский язык.
    - Не упоминай ID рецепта.
    - Не сравнивай рецепты между собой (не говори "этот лучше того").
    - Не выдумывай ингредиенты или шаги приготовления. Оперируй только предоставленными данными.
    - Не говори "в нашем списке" или "в найденных рецептах".
    - Не пересказывай запрос пользователя.
"""

        return await self._chat_with_model(prompt, temperature=0.45)

    async def _generate_no_results_response(
        self,
        user_message: str,
    ) -> str:

        prompt = f"""Пользователь спросил: "{user_message}"

    По этому запросу рецептов НЕ НАЙДЕНО.

    ТВОЯ ЗАДАЧА:
    1. Вежливо сообщи, что рецептов по запросу не найдено.
    2. Предложи изменить критерии: убрать часть ограничений, попробовать другие ингредиенты.
    3. НЕЛЬЗЯ предлагать конкретные рецепты, если их нет в наличии.
    4. НЕЛЬЗЯ говорить "можно приготовить X, Y, Z" — таких рецептов у нас нет.
    5. НЕЛЬЗЯ выдумывать названия блюд.

    Пример хорошего ответа:
    "К сожалению, по вашему запросу рецептов не найдено. Попробуйте расширить критерии поиска —
     например использовать более конкретные и ключевые слова близкие к тематике рецептов и ингредиентов"

    Плохой ответ (ЗАПРЕЩЕНО):
    "Можно приготовить салат оливье или холодный шоколадный мусс" — так нельзя, этих рецептов нет в наличии."""

        return await self._chat_with_model(prompt, temperature=0.3)

    async def _generate_refusal(self, user_message: str) -> str:
        """Генерирует вежливый отказ на запрос не о еде"""

        prompt = f"""Пользователь написал: "{user_message}"

    Вежливо ответь, что ты специализируешься только на поиске рецептов и не можешь помочь с этим вопросом.
    Предложи задать вопрос о еде или рецептах.
        """

        return await self._chat_with_model(prompt)

    async def _chat_with_model(
        self,
        prompt: str,
        temperature: float = 0.5,
        max_retries: int = 3
    ) -> str:
        url = f"{self.ollama_url}/api/chat"
        time_start = time.time()
        logger.info("Sending request to Ollama")

        system_prompt = (
            "Ты — дружелюбный матёрый шеф-повар. "
            "ОБЯЗАТЕЛЬНО отвечай ТОЛЬКО на русском языке. "
            "Если запрос пользователя содержал что-то нереалистичное "
            "(например, 'мясо демонов' или другие фантастические продукты) шутливо скажи, что таких рецептов нет "
            "и предложи поискать реальные блюда. "
            "ЗАПРЕЩЕНО самому генерировать рецепты."
            "ЗАПРЕЩЕНО сравнивать рецепты между собой, говорить 'этот лучше', 'более вкусное чем'. "
            "ЗАПРЕЩЕНО задавать риторические вопросы и отвечать на них же ('Почему подходит? Потому что...'). "
            "ЗАПРЕЩЕНО использовать конструкции 'Почему?', 'Чем хорош?', 'В чём плюс?' и подобные. "
            "ЗАПРЕЩЕНО упоминать ID рецептов."
            "Будь полезным, конкретным и дружелюбным. "
            "Используй эмодзи умеренно и только рядом с блюдом которое оно характеризует."
        )

        for attempt in range(max_retries):
            logger.info("Attempt %s", attempt + 1, extra={"attempt": attempt + 1})
            payload = {
                "model": "qwen2.5:7b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                }
            }

            try:
                async with aiohttp.ClientSession() as session, session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != status.HTTP_200_OK:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)
                            continue
                        return "Извините, произошла ошибка при генерации ответа."

                    result = await response.json()
                    content = result["message"]["content"]

                    has_cjk = self._contains_cjk(content)

                    has_english = self._contains_unwanted_english(content)

                    if not has_cjk and not has_english:
                        logger.info(f"Chat completed in {time.time() - time_start:.2f} seconds")
                        return content

                    if has_cjk:
                        logger.warning("Attempt: CJK found, retrying...", attempt + 1)
                    if has_english:
                        logger.warning("Attempt: English words found, retrying...", attempt + 1)
                        prompt = (
                            f"ПЕРЕПИШИ ответ полностью на русском. "
                            f"В предыдущем ответе были английские слова — это НЕДОПУСТИМО.\n\n"
                            f"Исходный запрос:\n{prompt}"
                        )

                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.5)
                        continue

            except (TimeoutError, aiohttp.ClientError) as e:
                logger.error("Attempt %s failed: %s", attempt + 1, e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                return "Извините, произошла ошибка при генерации ответа."

        logger.warning("All retries exhausted, cleaning response")
        content = self._filter_cjk(content)
        return content or "Извините, не удалось сгенерировать корректный ответ."

    def _contains_unwanted_english(self, text: str) -> bool:
        forbidden = [
            "something", "anything", "maybe", "however", "therefore",
            "moreover", "nevertheless", "meanwhile", "furthermore",
            "here is", "here are", "based on", "in this", "that is"
        ]
        text_lower = text.lower()
        return any(word in text_lower for word in forbidden)

    def _contains_cjk(self, text: str) -> bool:
        cjk_pattern = re.compile(
            r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7AF]"
        )
        return bool(cjk_pattern.search(text))

    def _filter_cjk(self, text: str) -> str:
        cjk_pattern = re.compile(
            r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7AF]"
        )
        cleaned = cjk_pattern.sub("", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        if not cleaned:
            return "Извините, не удалось сгенерировать корректный ответ. Попробуйте переформулировать запрос."

        return cleaned
