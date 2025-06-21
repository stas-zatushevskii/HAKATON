from openai import OpenAI
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # если используешь POST без CSRF-токена
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.conf import settings

# Initialize OpenAI client with API key
client = OpenAI(api_key="")

@csrf_exempt
@require_http_methods(["POST"])
def generate_learning_plan(request):
    try:
        data = json.loads(request.body)

        topic = data.get("topic", "Программирование на Python")
        level = data.get("level", "полный новичок")
        tone = data.get("tone", "дружелюбный, с аналогиями")

        prompt = f"""
Ты опытный наставник по теме "{topic}". Твоя задача — пошагово провести ученика от текущего уровня ("{level}") до уверенного владения темой. Ответ верни строго в JSON-структуре, пригодной для API-интерфейса.

Ответ должен содержать:

[
  {{
    "step_number": 1,
    "title": "Название этапа",
    "description": "Краткое описание зачем изучать эту тему",
    "theory_summary": ["Основные теоретические идеи", "понятия", "факты"],
    "exercises": ["Мини-задание 1", "Мини-задание 2"],
    "self_check_questions": ["Вопрос 1", "Вопрос 2"],
    "challenge_task": "Задание с повышенной сложностью",
    "expected_skill": "Какой навык будет сформирован",
    "real_world_connection": "Как это применимо в реальности",
    "analogy": "Пример или аналогия для лучшего понимания"
  }}
]

Тема: {topic}  
Уровень: {level}  
Желаемый стиль: {tone} (например, разговорный, академический, с юмором)

Ответ не должен содержать никакого пояснительного текста вне JSON. Только строго массив объектов — один объект = один шаг. Каждый шаг должен логично следовать за предыдущим.

Начни с самого базового и двигайся к сложному.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты ассистент по обучению с уклоном в структурированные пошаговые планы."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        result_text = response.choices[0].message.content

        # Clean the response text to remove markdown formatting
        cleaned_text = result_text.strip()
        
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("json"):
            cleaned_text = cleaned_text[4:]
        
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        
        cleaned_text = cleaned_text.strip()

        try:
            learning_steps = json.loads(cleaned_text)
            return JsonResponse({"success": True, "data": learning_steps}, status=200, json_dumps_params={'ensure_ascii': False, 'indent': 2})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Ошибка при парсинге JSON из ответа OpenAI", "raw": result_text, "cleaned": cleaned_text}, status=500)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

def test_learning_plan_view(request):
    """HTML view to test the learning plan generation with failsafes"""
    return render(request, 'learning_plan_test.html')


@csrf_exempt
@require_http_methods(["POST"])
def process_user_answer(request):
    try:
        data = json.loads(request.body)

        user_answer = data.get("answer")
        question = data.get("question")
        topic = data.get("topic", "Общая тема обучения")
        tone = data.get("tone", "доброжелательный, но точный")

        if not user_answer or not question:
            return JsonResponse({"success": False, "error": "Не передан вопрос или ответ пользователя."}, status=400)

        prompt = f"""
Ты преподаватель по теме "{topic}". Сейчас тебе нужно проверить ответ ученика на следующий вопрос.

Вопрос: "{question}"

Ответ ученика: "{user_answer}"

Твоя задача —:
- Точно, но доброжелательно оценить ответ
- Указать, что верно, а что требует исправления
- Если ответ частично верный — предложи, как улучшить
- Приведи идеальный пример ответа
- Используй стиль: {tone}

Верни результат строго в следующем JSON-формате:

{{
  "feedback": "Краткий фидбэк по ответу",
  "corrections": ["Замечание 1", "Замечание 2"],
  "suggested_answer": "Идеальный ответ на этот вопрос",
  "encouragement": "Фраза поддержки, мотивационная"
}}

Не добавляй ничего вне JSON. Только чистый JSON-объект.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты AI-наставник, дающий обратную связь на ответы учеников."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        result_text = response.choices[0].message.content
        cleaned_text = result_text.strip()

        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("json"):
            cleaned_text = cleaned_text[4:]

        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        try:
            feedback_data = json.loads(cleaned_text)
            return JsonResponse({"success": True, "feedback": feedback_data}, status=200, json_dumps_params={'ensure_ascii': False, 'indent': 2})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Ошибка парсинга JSON из ответа GPT", "raw": result_text, "cleaned": cleaned_text}, status=500)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
