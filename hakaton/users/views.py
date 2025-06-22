from openai import OpenAI
import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from decouple import config

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=config('OPENAI_API_KEY'))

def json_login_required(view_func):
    """Custom decorator that returns JSON error for unauthenticated users"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "Authentication required"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

@csrf_exempt
@json_login_required
@require_http_methods(["POST"])
def generate_learning_plan(request):
    try:
        data = json.loads(request.body)

        topic = data.get("topic", "Python Programming")
        level = data.get("level", "complete beginner")
        tone = data.get("tone", "friendly, with analogies")

        prompt = f"""
        You are a senior software engineer and technical lead with 10+ years of industry experience in "{topic}". Create a comprehensive, project-driven learning path that mirrors real software development workflows and industry practices. Focus on building production-ready applications that solve actual business problems. Return the answer strictly in a JSON format suitable for an API.

        Each step must be practical, industry-focused and contain:

        [
          {{
            "step_number": 1,
            "title": "Stage Title",
            "description": "A brief description of why this topic should be studied at this stage",
            "theory_summary": [
              "A detailed explanation of the key theoretical idea",
              "Real-world examples",
              "Connection to other concepts in the topic",
              "Small facts or principles that are often overlooked"
            ],
            "practical_task": {{
              "task_description": "A complete real-world programming project that simulates actual industry work (e.g., building APIs, implementing authentication, database design, deployment)",
              "input_format": "Technical specifications and requirements",
              "expected_output": "Working software solution with code repository",
              "evaluation_criteria": "Code quality, functionality, scalability, security practices, and industry standards compliance"
            }},
            "self_check_questions": [
              "Technical interview question that tests deep understanding",
              "Debugging scenario or code review question",
              "System design or architecture question"
            ],
            "expected_skill": "Specific programming competency that would be valuable to employers",
            "real_world_connection": "How this skill is used in production systems, startups, or enterprise environments",
            "analogy": "Technical analogy that relates to software architecture, development patterns, or industry practices"
          }}
        ]

        **Rules:**
        - Each step represents a complete software development milestone.
        - Focus on building real applications that could be deployed and used.
        - Include modern development practices: version control, testing, CI/CD, containerization.
        - Practical tasks should result in portfolio-worthy projects.
        - Emphasize industry-standard tools, frameworks, and methodologies.
        - Do not include any explanatory phrases outside of the JSON. Only a strict array of JSON objects.

        Topic: {topic}  
        Level: {level}  
        Desired tone: {tone} (but maintain technical accuracy and industry focus)

        Structure the learning path like a real software development career progression, from junior to senior level skills.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "You are a learning assistant focused on structured step-by-step plans."},
            {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
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

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def test_learning_plan_view(request):
    """HTML view to test the learning plan generation with failsafes"""
    return render(request, 'learning_plan_test.html')


@csrf_exempt
@json_login_required
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
    Ești un profesor pe tema "{topic}". Acum trebuie să verifici răspunsul unui student la următoarea întrebare.

    Întrebare: "{question}"

    Răspunsul studentului: "{user_answer}"

    Sarcina ta este să:
    - Evaluezi răspunsul cu precizie, dar într-un mod prietenos
    - Indici ce este corect și ce necesită corectare
    - Dacă răspunsul este parțial corect, sugerezi cum poate fi îmbunătățit
    - Oferi un exemplu de răspuns ideal
    - Folosește stilul: {tone}

    Returnează rezultatul strict în următorul format JSON:

    {{
      "feedback": "Feedback scurt despre răspuns",
      "corrections": ["Observația 1", "Observația 2"],
      "suggested_answer": "Răspunsul ideal la această întrebare",
      "encouragement": "O frază de încurajare, motivațională"
    }}

    Nu adăuga nimic în afara JSON-ului. Doar un obiect JSON pur.
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

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
@json_login_required
@require_http_methods(["POST"])
def create_challenge_from_plan(request):
    """Create coding challenges based on learning plan steps"""
    try:
        data = json.loads(request.body)
        
        step_data = data.get("step_data")
        topic = data.get("topic", "Programming")
        level = data.get("level", "complete beginner")
        
        # Map learning plan levels to challenge difficulties
        level_to_difficulty = {
            "complete beginner": "easy",
            "полный новичок": "easy",
            "beginner": "easy",
            "базовый": "easy",
            "basic": "easy",
            "intermediate": "medium",
            "средний": "medium",
            "medium": "medium",
            "advanced": "hard",
            "продвинутый": "hard",
            "hard": "hard",
            "expert": "hard"
        }
        
        difficulty = level_to_difficulty.get(level.lower(), "easy")
        
        if not step_data:
            return JsonResponse({"success": False, "error": "No step data provided"}, status=400)
            
        step_title = step_data.get("title", "Programming Challenge")
        step_description = step_data.get("description", "")
        practical_task = step_data.get("practical_task", {})
        
        prompt = f"""
    You are a senior software architect. Create a real-world programming project that is STRICTLY appropriate for the difficulty level "{difficulty}".

    Learning Step: "{step_title}"
    Description: "{step_description}"
    Topic: "{topic}"
    Difficulty: "{difficulty}"

    DIFFICULTY GUIDELINES:
    - EASY: Simple console applications, basic scripts, single-file programs with 20-50 lines of code (1-3 hours)
    - MEDIUM: Small web apps, basic APIs, simple databases, projects with 2-5 files (4-8 hours)
    - HARD: Complex systems, microservices, enterprise applications, full-stack projects (10-20 hours)

    For "{difficulty}" level, create a project that matches these constraints:
    
    EASY: Simple programming exercises like calculators, text processors, basic games, file readers
    MEDIUM: Basic web forms, simple REST APIs, small databases, basic authentication
    HARD: Enterprise systems, complex architectures, scalable applications, advanced patterns

    TIME ESTIMATION:
    - EASY: 1-3 hours
    - MEDIUM: 4-8 hours  
    - HARD: 10-20 hours

    Return the result in this exact JSON format:

    {{
      "title": "Clear, specific project title",
      "description": "Detailed project description explaining the real-world problem it solves",
      "app_type": "Type of application (web app, mobile app, desktop tool, etc.)",
      "use_case": "Real-world scenario where this app would be useful",
      "features": [
        "Key feature 1",
        "Key feature 2",
        "Key feature 3"
      ],
      "user_stories": [
        "As a [user type], I want to [action] so that [benefit]",
        "As a [user type], I want to [action] so that [benefit]"
      ],
      "technical_requirements": [
        "Technical requirement 1",
        "Technical requirement 2"
      ],
      "implementation_steps": [
        {{
          "step": 1,
          "title": "Step title",
          "description": "What to implement in this step",
          "deliverable": "What should be completed"
        }},
        {{
          "step": 2,
          "title": "Step title", 
          "description": "What to implement in this step",
          "deliverable": "What should be completed"
        }}
      ],
      "sample_data": "Example data or scenarios to test the app",
      "success_criteria": [
        "Criterion 1 for successful completion",
        "Criterion 2 for successful completion"
      ],
      "hints": [
        "Helpful implementation hint 1",
        "Helpful implementation hint 2"
      ],
      "tags": ["tag1", "tag2", "tag3"],
      "estimated_time": 2,
      "concepts_applied": ["concept1", "concept2"],
      "potential_extensions": [
        "Extension idea 1",
        "Extension idea 2"
      ]
    }}

    IMPORTANT: Match the complexity to the difficulty level. For EASY difficulty, focus on simple, educational projects that teach fundamentals. For MEDIUM, build practical applications. For HARD, create enterprise-level solutions.
    
    Ensure the project scope, technical requirements, and implementation steps are appropriate for someone at the "{difficulty}" level.
    """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert programming instructor who creates engaging coding challenges."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        result_text = response.choices[0].message.content
        cleaned_text = result_text.strip()
        
        # Clean JSON response
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("json"):
            cleaned_text = cleaned_text[4:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        try:
            challenge_data = json.loads(cleaned_text)
            
            # Save challenge to database
            from tasks.models import Challenge
            challenge = Challenge.objects.create(
                title=challenge_data.get("title", step_title),
                description=challenge_data.get("description", ""),
                difficulty=difficulty,
                created_by=request.user,
                sample_input=challenge_data.get("sample_input", ""),
                sample_output=challenge_data.get("sample_output", ""),
                tags=", ".join(challenge_data.get("tags", [])),
                time_limit=max(1, int(challenge_data.get("estimated_time", 60))),  # Ensure minimum 1 hour
                points=100 if difficulty == "easy" else 300 if difficulty == "medium" else 500
            )
            
            challenge_data["challenge_id"] = challenge.id
            challenge_data["challenge_url"] = f"/tasks/{challenge.id}/"
            
            return JsonResponse({
                "success": True, 
                "challenge": challenge_data,
                "message": "Challenge created successfully!"
            }, status=200, json_dumps_params={'ensure_ascii': False, 'indent': 2})
            
        except json.JSONDecodeError as e:
            return JsonResponse({
                "success": False, 
                "error": f"JSON parsing error: {str(e)}", 
                "raw": result_text, 
                "cleaned": cleaned_text
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@json_login_required
@require_http_methods(["POST"])
def evaluate_solution(request):
    """Evaluate user's solution to a coding challenge"""
    try:
        data = json.loads(request.body)
        
        challenge_id = data.get("challenge_id")
        user_solution = data.get("solution")
        programming_language = data.get("language", "python")
        
        if not challenge_id or not user_solution:
            return JsonResponse({"success": False, "error": "Missing challenge ID or solution"}, status=400)
        
        # Get challenge from database
        from tasks.models import Challenge
        try:
            challenge = Challenge.objects.get(id=challenge_id)
        except Challenge.DoesNotExist:
            return JsonResponse({"success": False, "error": "Challenge not found"}, status=404)

        prompt = f"""
You are a senior software engineering manager evaluating a production code submission for a critical enterprise system.

Challenge: "{challenge.title}"
Challenge Description: "{challenge.description}"
Sample Input: "{challenge.sample_input}"
Expected Output: "{challenge.sample_output}"

Student's Solution ({programming_language}):
```{programming_language}
{user_solution}
```

Evaluate this solution as if it were going into a production system serving millions of users. Consider scalability, security, error handling, code maintainability, and enterprise standards. Provide feedback in this exact JSON format:

{{
  "score": "score from 0-100",
  "status": "passed|failed|partial",
  "feedback": {{
    "overall": "Overall assessment of the solution",
    "correctness": "Does the solution solve the problem correctly?",
    "code_quality": "Assessment of code structure, readability, efficiency",
    "improvements": [
      "Specific improvement suggestion 1",
      "Specific improvement suggestion 2"
    ],
    "positive_points": [
      "What the student did well 1",
      "What the student did well 2"
    ]
  }},
  "test_results": [
    {{
      "test_case": "Description of test case",
      "expected": "Expected result",
      "actual": "What the code would produce (or error)",
      "passed": true/false
    }}
  ],
  "next_steps": [
    "Suggestion for what to study next",
    "Resources or topics to explore"
  ]
}}

Be rigorous in evaluation, focusing on production-readiness, enterprise standards, and industry best practices. Consider security vulnerabilities, performance bottlenecks, and maintainability issues.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful programming instructor providing detailed code evaluation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        result_text = response.choices[0].message.content
        cleaned_text = result_text.strip()
        
        # Clean JSON response
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("json"):
            cleaned_text = cleaned_text[4:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        try:
            evaluation_data = json.loads(cleaned_text)
            
            # Save submission to database
            from tasks.models import Submission
            submission = Submission.objects.create(
                user=request.user,
                challenge=challenge,
                solution_code=user_solution,
                programming_language=programming_language,
                status=evaluation_data.get('status', 'failed'),
                score=int(evaluation_data.get('score', 0)),
                overall_feedback=evaluation_data.get('feedback', {}).get('overall', ''),
                correctness_feedback=evaluation_data.get('feedback', {}).get('correctness', ''),
                code_quality_feedback=evaluation_data.get('feedback', {}).get('code_quality', ''),
                improvements=evaluation_data.get('feedback', {}).get('improvements', []),
                positive_points=evaluation_data.get('feedback', {}).get('positive_points', []),
                test_results=evaluation_data.get('test_results', []),
                next_steps=evaluation_data.get('next_steps', [])
            )
            
            # Add submission info to response
            evaluation_data['submission_id'] = submission.id
            evaluation_data['is_best'] = submission.is_best
            
            return JsonResponse({
                "success": True, 
                "evaluation": evaluation_data
            }, status=200, json_dumps_params={'ensure_ascii': False, 'indent': 2})
            
        except json.JSONDecodeError as e:
            return JsonResponse({
                "success": False, 
                "error": f"JSON parsing error: {str(e)}", 
                "raw": result_text, 
                "cleaned": cleaned_text
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def challenge_creator_view(request):
    """HTML view for the challenge creator interface"""
    return render(request, 'challenge_creator.html')


@login_required
def solution_evaluator_view(request):
    """HTML view for the solution evaluator interface"""
    from tasks.models import Challenge
    challenges = Challenge.objects.filter(status='active').order_by('-created_at')[:20]
    
    # Get pre-selected challenge from URL parameter
    selected_challenge_id = request.GET.get('challenge')
    selected_challenge = None
    if selected_challenge_id:
        try:
            selected_challenge = Challenge.objects.get(id=selected_challenge_id, status='active')
        except Challenge.DoesNotExist:
            pass
    
    context = {
        'challenges': challenges,
        'selected_challenge': selected_challenge
    }
    return render(request, 'solution_evaluator.html', context)