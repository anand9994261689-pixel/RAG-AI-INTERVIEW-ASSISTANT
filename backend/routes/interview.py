from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.rag.generator import generate_questions as llm_generate_questions, evaluate_answer, generate_followup
from backend.rag.retriever import retrieve_context

router = APIRouter()

class EvaluationRequest(BaseModel):
    question: str
    answer: str

class FollowupRequest(BaseModel):
    question: str
    answer: str

@router.get("/generate-questions")
async def generate_questions(request: Request):
    """
    Generates 5 personalized interview questions based on Resume and Job Description context.
    """
    # Verify vector store is loaded
    if not hasattr(request.app.state, "resume_text") or not request.app.state.resume_text:
        raise HTTPException(
            status_code=400, 
            detail="No files uploaded. Please upload a Resume and Job Description first."
        )
        
    try:
        resume_text = request.app.state.resume_text
        jd_text = request.app.state.jd_text
        
        # Call LLM to generate questions
        questions = llm_generate_questions(resume_text, jd_text)
        
        if not questions:
            raise HTTPException(status_code=500, detail="Failed to generate questions. Please try again.")
            
        # Store in state
        request.app.state.questions = questions
        request.app.state.history = []  # Clear previous history
        
        return {
            "status": "success",
            "questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

@router.post("/evaluate")
async def evaluate(request: Request, body: EvaluationRequest):
    """
    Evaluates a candidate's answer to a question using retrieved RAG context.
    """
    if not hasattr(request.app.state, "index") or request.app.state.index is None:
        raise HTTPException(
            status_code=400, 
            detail="FAISS index is not initialized. Please upload a Resume and Job Description first."
        )
        
    try:
        # Retrieve context from FAISS based on the question
        query = f"Question: {body.question}\nAnswer: {body.answer}"
        context = retrieve_context(
            query=query, 
            index=request.app.state.index, 
            chunks=request.app.state.chunks, 
            k=3
        )
        
        # Evaluate using generator
        evaluation = evaluate_answer(body.question, body.answer, context)
        
        # Save to interview history
        history_item = {
            "question": body.question,
            "answer": body.answer,
            "score": evaluation["score"],
            "strengths": evaluation["strengths"],
            "weaknesses": evaluation["weaknesses"],
            "improvements": evaluation["improvements"]
        }
        request.app.state.history.append(history_item)
        
        return {
            "status": "success",
            "evaluation": evaluation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answer: {str(e)}")

@router.post("/generate-followup")
async def generate_followup_question(request: Request, body: FollowupRequest):
    """
    Generates a follow-up question when the candidate's answer score is low.
    """
    if not hasattr(request.app.state, "index") or request.app.state.index is None:
        raise HTTPException(
            status_code=400, 
            detail="FAISS index is not initialized. Please upload a Resume and Job Description first."
        )
        
    try:
        # Retrieve context from FAISS
        query = f"Question: {body.question}\nAnswer: {body.answer}"
        context = retrieve_context(
            query=query, 
            index=request.app.state.index, 
            chunks=request.app.state.chunks, 
            k=2
        )
        
        # Generate follow-up
        followup = generate_followup(body.question, body.answer, context)
        
        return {
            "status": "success",
            "followup": followup
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating follow-up question: {str(e)}")
