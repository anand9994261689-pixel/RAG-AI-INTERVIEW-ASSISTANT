import os
import re
import json
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
import httpx

load_dotenv()

# Determine LLM configuration
def get_llm_config() -> Dict[str, str]:
    """
    Dynamically loads and retrieves the latest LLM config from environment.
    This ensures changes in .env are picked up without requiring server restarts.
    """
    load_dotenv(override=True)
    return {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "gemini").lower(),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "GEMINI_MODEL": os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "llama3"),
    }

# Keep global references initialized on startup for compatibility
_initial_config = get_llm_config()
LLM_PROVIDER = _initial_config["LLM_PROVIDER"]
GEMINI_API_KEY = _initial_config["GEMINI_API_KEY"]
GEMINI_MODEL = _initial_config["GEMINI_MODEL"]
OPENAI_API_KEY = _initial_config["OPENAI_API_KEY"]
OPENAI_MODEL = _initial_config["OPENAI_MODEL"]
OLLAMA_BASE_URL = _initial_config["OLLAMA_BASE_URL"]
OLLAMA_MODEL = _initial_config["OLLAMA_MODEL"]

# Initialize Gemini on startup if configured
if LLM_PROVIDER == "gemini" and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def call_llm(prompt: str, system_instruction: str = None) -> str:
    """
    Unified LLM caller that handles Gemini, OpenAI, and Ollama.
    Loads configurations dynamically and implements robust rate limit retries & model fallbacks.
    """
    config = get_llm_config()
    provider = config["LLM_PROVIDER"]
    
    current_gemini_model = config["GEMINI_MODEL"]
    fallback_attempted = False
    max_retries = 3
    backoff_factor = 2

    for attempt in range(max_retries):
        try:
            if provider == "gemini":
                api_key = config["GEMINI_API_KEY"]
                if not api_key:
                    raise ValueError("GEMINI_API_KEY not found in environment variables.")
                # Dynamically configure API key to support runtime updates
                genai.configure(api_key=api_key)
                
                if system_instruction:
                    model = genai.GenerativeModel(
                        model_name=current_gemini_model,
                        system_instruction=system_instruction
                    )
                else:
                    model = genai.GenerativeModel(model_name=current_gemini_model)
                
                response = model.generate_content(prompt)
                return response.text.strip()
                
            elif provider == "openai":
                openai_key = config["OPENAI_API_KEY"]
                if not openai_key:
                    raise ValueError("OPENAI_API_KEY not found in environment variables.")
                client = OpenAI(api_key=openai_key)
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                
                response = client.chat.completions.create(
                    model=config["OPENAI_MODEL"],
                    messages=messages,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
                
            elif provider == "ollama":
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                
                payload = {
                    "model": config["OLLAMA_MODEL"],
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7
                    }
                }
                response = httpx.post(f"{config['OLLAMA_BASE_URL']}/api/chat", json=payload, timeout=60.0)
                response.raise_for_status()
                res_json = response.json()
                return res_json["message"]["content"].strip()
                
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
                
        except Exception as e:
            err_msg = str(e)
            is_rate_limit = "429" in err_msg or "ResourceExhausted" in err_msg or "rate_limit" in err_msg.lower()
            
            # If the quota was exceeded on gemini-3.5-flash/gemini-2.5-flash, try falling back to gemini-2.5-flash-lite
            if provider == "gemini" and is_rate_limit and not fallback_attempted and current_gemini_model != "gemini-2.5-flash-lite":
                print(f"[LLM Rate Limit 429] Model '{current_gemini_model}' failed due to quota/rate limit. "
                      f"Attempting automatic fallback to 'gemini-2.5-flash-lite'...")
                current_gemini_model = "gemini-2.5-flash-lite"
                fallback_attempted = True
                continue
                
            if is_rate_limit and attempt < max_retries - 1:
                # Add extra delay to allow the server reset time
                sleep_time = (backoff_factor ** (attempt + 1)) + 8
                print(f"[LLM Rate Limit 429] Retrying call in {sleep_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(sleep_time)
                continue
                
            provider_name = provider.upper()
            raise RuntimeError(f"{provider_name} API call failed: {err_msg}")

def generate_questions(resume_text: str, jd_text: str) -> List[str]:
    """
    Generates 5 personalized interview questions based on Resume and Job Description context.
    """
    system_instruction = (
        "You are a professional HR + technical interviewer.\n\n"
        "Your goal is to conduct a simple, human-like interview based on the candidate's resume and job description.\n\n"
        "Behavior:\n"
        "- Ask one question at a time\n"
        "- Keep questions simple and natural (like a real HR)\n"
        "- Mix basic technical and HR questions\n"
        "- Focus on candidate projects, skills, and tech stack\n"
        "- Do not ask overly complex or theoretical questions\n"
        "- Do not explain anything\n"
        "- Do not give hints\n\n"
        "Tone:\n"
        "- Friendly but professional\n"
        "- Short and clear\n"
        "- Human-like (not robotic)"
    )
    
    short_context = f"Resume Summary:\n{resume_text[:1200]}...\n\nJob Description:\n{jd_text[:1200]}..."
    
    prompt = f"""
Act as an HR interviewer.

Context:
{short_context}

Generate 5 simple interview questions.

Rules:
- Ask like a human (not AI)
- Focus on:
  - Projects
  - Tech stack
  - Experience
- Include questions like:
  - "What technologies did you use in your project?"
  - "Explain your role in the project"
  - "What challenges did you face?"
- Keep questions short and clear

Output:
1.
2.
3.
4.
5.
"""
    
    response_text = call_llm(prompt, system_instruction)
    
    # Parse numbered list
    questions = []
    lines = response_text.split('\n')
    for line in lines:
        line = line.strip()
        # Match standard patterns like "1. Question text" or "1) Question text"
        match = re.match(r'^\d+[\.\)\-\s]+(.*)', line)
        if match:
            question_text = match.group(1).strip()
            if question_text:
                questions.append(question_text)
        elif line and len(line) > 10 and not line.startswith(('Here', 'Sure', 'Below')):
            questions.append(line)
            
    # Return exactly up to 5 questions
    return questions[:5]

def evaluate_answer(question: str, answer: str, context: str = "") -> Dict[str, Any]:
    """
    Evaluates a candidate's answer against a question, using index/RAG context if available.
    """
    system_instruction = (
        "You are an HR + technical evaluation system.\n\n"
        "Your task is to evaluate the candidate's answer based on the question and RAG context.\n"
        "Do NOT ask any follow-up questions. Only return the evaluation in the requested output format."
    )
    
    prompt = f"""
Evaluate the answer using the following RAG context if relevant.

RAG Context:
{context}

Q: {question}
A: {answer}

Give:

Score: X/10
Strength: one line
Weakness: one line
Improve: one line
"""

    response_text = call_llm(prompt, system_instruction)
    
    # Parse fields
    score = 5.0
    strengths = []
    weaknesses = []
    improvements = []
    
    # Search for score
    score_match = re.search(r'Score:\s*(\d+(\.\d+)?)\s*/\s*10', response_text, re.IGNORECASE)
    if not score_match:
        score_match = re.search(r'Score:\s*(\d+(\.\d+)?)', response_text, re.IGNORECASE)
        
    if score_match:
        try:
            score = float(score_match.group(1))
        except ValueError:
            score = 5.0
            
    # Parse line by line to extract Strength, Weakness, and Improve
    lines = response_text.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Match "Strength: <content>"
        strength_match = re.match(r'^strength(?:s)?:\s*(.*)', line_stripped, re.IGNORECASE)
        if strength_match:
            val = strength_match.group(1).strip().lstrip("-*• ").strip()
            if val:
                strengths.append(val)
            continue
            
        # Match "Weakness: <content>"
        weakness_match = re.match(r'^weakness(?:es)?:\s*(.*)', line_stripped, re.IGNORECASE)
        if weakness_match:
            val = weakness_match.group(1).strip().lstrip("-*• ").strip()
            if val:
                weaknesses.append(val)
            continue
            
        # Match "Improve: <content>" or "Improvement: <content>"
        improve_match = re.match(r'^(?:improvement(?:s)?|improve):\s*(.*)', line_stripped, re.IGNORECASE)
        if improve_match:
            val = improve_match.group(1).strip().lstrip("-*• ").strip()
            if val:
                improvements.append(val)
            continue
                     
    # Fallback to defaults if parsing fails completely
    if not strengths:
        strengths = ["Answer provided contains basic details."]
    if not weaknesses:
        weaknesses = ["Could be more comprehensive."]
    if not improvements:
        improvements = ["Elaborate with specific technical examples and methodologies."]
        
    return {
        "score": score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "improvements": improvements,
        "raw_response": response_text
    }

def generate_followup(question: str, answer: str, context: str = "") -> str:
    """
    Generates a simple, human-like follow-up question when the candidate's answer is weak.
    """
    system_instruction = (
        "You are a professional HR + technical interviewer.\n\n"
        "Your goal is to conduct a simple, human-like interview based on the candidate's resume and job description.\n\n"
        "Behavior:\n"
        "- Ask one question at a time\n"
        "- Keep questions simple and natural (like a real HR)\n"
        "- Mix basic technical and HR questions\n"
        "- Focus on candidate projects, skills, and tech stack\n"
        "- Do not ask overly complex or theoretical questions\n"
        "- Do not explain anything\n"
        "- Do not give hints\n\n"
        "Tone:\n"
        "- Friendly but professional\n"
        "- Short and clear\n"
        "- Human-like (not robotic)"
    )
    
    prompt = f"""
RAG Context:
{context}

Previous Question: {question}
Candidate's Weak Answer: {answer}

Rules:
- Ask a follow-up question to probe their understanding or clarify their weak explanation.
- Keep the tone professional, friendly, and human-like (not robotic).
- Do NOT explain anything or give hints.
- Output ONLY the follow-up question.
"""
    return call_llm(prompt, system_instruction)

def generate_final_feedback(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregates the interview chat history and provides a comprehensive feedback evaluation.
    """
    formatted_history = ""
    total_score = 0
    num_questions = 0
    
    for i, item in enumerate(history):
        formatted_history += f"Q{i+1}: {item.get('question')}\n"
        formatted_history += f"A{i+1}: {item.get('answer')}\n"
        formatted_history += f"Evaluation: Score {item.get('score')}/10\n"
        formatted_history += f"Strengths: {', '.join(item.get('strengths', []))}\n"
        formatted_history += f"Weaknesses: {', '.join(item.get('weaknesses', []))}\n"
        formatted_history += f"Improvements: {', '.join(item.get('improvements', []))}\n\n"
        
        total_score += item.get('score', 0)
        num_questions += 1
        
    avg_score_10 = (total_score / num_questions) if num_questions > 0 else 0
    # Scale to 100
    overall_score = round(avg_score_10 * 10)
    
    system_instruction = (
        "You are a senior hiring manager reviewing interview performance notes.\n"
        "Provide a professional, clear, and realistic evaluation."
    )
    
    prompt = f"""
You are a hiring manager.

Based on all answers and evaluations, give:
- Overall Score (out of 100)
- Strengths (List)
- Weaknesses (List)
- Final suggestion
- Hiring decision (Yes / No / Maybe)

Here is the Interview History:
{formatted_history}

Output format strictly as follows:
Overall Score: {overall_score}
Strengths:
- Strength 1
- Strength 2
...
Weaknesses:
- Weakness 1
- Weakness 2
...
Suggestions:
- Suggestion 1
- Suggestion 2
...
Hiring Decision: <Yes, No, or Maybe>
"""
    
    response_text = call_llm(prompt, system_instruction)
    
    # Parse output
    strengths = []
    weaknesses = []
    suggestions = []
    decision = "Maybe"
    
    sections = re.split(r'(Strengths:|Weaknesses:|Suggestions:|Hiring Decision:)', response_text, flags=re.IGNORECASE)
    
    current_section = None
    for item in sections:
        item_lower = item.lower().strip()
        if item_lower == 'strengths:':
            current_section = 'strengths'
        elif item_lower == 'weaknesses:':
            current_section = 'weaknesses'
        elif item_lower == 'suggestions:':
            current_section = 'suggestions'
        elif item_lower == 'hiring decision:':
            current_section = 'decision'
        else:
            if current_section and item.strip():
                points = [p.strip().lstrip('-* ').strip() for p in item.strip().split('\n') if p.strip()]
                points = [p for p in points if p]
                if current_section == 'strengths':
                    strengths.extend(points)
                elif current_section == 'weaknesses':
                    weaknesses.extend(points)
                elif current_section == 'suggestions':
                    suggestions.extend(points)
                elif current_section == 'decision':
                    decision = item.strip().replace('.', '')
                    
    # Validate parsed decision
    decision_clean = decision.lower()
    if "yes" in decision_clean:
        decision = "Yes"
    elif "no" in decision_clean:
        decision = "No"
    else:
        decision = "Maybe"
        
    return {
        "overall_score": overall_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "decision": decision,
        "raw_response": response_text
    }
