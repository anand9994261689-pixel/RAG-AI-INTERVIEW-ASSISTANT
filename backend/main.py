from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from backend.routes.upload import router as upload_router
from backend.routes.interview import router as interview_router
from backend.routes.feedback import router as feedback_router

app = FastAPI(
    title="AI Interview Preparation Assistant API",
    description="Backend services for RAG-based AI Mock Interviews, Answer Evaluation, and Feedback Aggregation.",
    version="1.0.0"
)

# Enable CORS for frontend integration (Streamlit default port is 8501, but we allow all localhost for flexibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize application in-memory state
app.state.resume_text = ""
app.state.jd_text = ""
app.state.index = None
app.state.chunks = []
app.state.questions = []
app.state.history = []

# Register routes
app.include_router(upload_router, tags=["Upload"])
# Prefix interview endpoints or register directly.
# The user request specified:
# 1. POST /upload
# 2. GET /generate-questions
# 3. POST /evaluate
# 4. GET /feedback
# To match this flat structure, we register the routes without prefixes.
app.include_router(interview_router, tags=["Interview"])
app.include_router(feedback_router, tags=["Feedback"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "AI Interview Assistant FastAPI Backend is active.",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    # Start the FastAPI server using uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
