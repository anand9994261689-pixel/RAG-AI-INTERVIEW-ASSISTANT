from fastapi import APIRouter, Request, HTTPException
from backend.rag.generator import generate_final_feedback

router = APIRouter()

@router.get("/feedback")
@router.get("/final-feedback")
async def get_feedback(request: Request):
    """
    Aggregates the individual interview evaluation scores and generates a hiring decision and constructive summary feedback.
    """
    if not hasattr(request.app.state, "history") or not request.app.state.history:
        raise HTTPException(
            status_code=400, 
            detail="No interview history found. Please complete the interview first."
        )
        
    try:
        history = request.app.state.history
        
        # Calculate scores and final decision using the LLM aggregator
        feedback_report = generate_final_feedback(history)
        
        # Add summary data
        detailed_scores = [
            {
                "question": item["question"],
                "answer": item["answer"],
                "score": item["score"],
                "strengths": item["strengths"],
                "weaknesses": item["weaknesses"],
                "improvements": item["improvements"]
            }
            for item in history
        ]
        
        return {
            "status": "success",
            "overall_score": feedback_report["overall_score"],
            "strengths": feedback_report["strengths"],
            "weaknesses": feedback_report["weaknesses"],
            "suggestions": feedback_report["suggestions"],
            "decision": feedback_report["decision"],
            "detailed_evaluations": detailed_scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error compiling final feedback: {str(e)}")
