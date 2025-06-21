import openai
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # если используешь POST без CSRF-токена
from django.views.decorators.http import require_http_methods

# Обязательно настрой свой API-ключ через переменные окружения или Django settings
openai.api_key = ""

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

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты ассистент по обучению с уклоном в структурированные пошаговые планы."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        result_text = response['choices'][0]['message']['content']

        try:
            learning_steps = json.loads(result_text)
            return JsonResponse({"success": True, "data": learning_steps}, status=200, json_dumps_params={'ensure_ascii': False, 'indent': 2})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Ошибка при парсинге JSON из ответа OpenAI", "raw": result_text}, status=500)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)