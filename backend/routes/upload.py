from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException
from backend.utils.parser import extract_text_from_pdf
from backend.utils.chunker import split_text_into_chunks
from backend.rag.embed import build_faiss_index

router = APIRouter()

@router.post("/upload")
async def upload_files(
    request: Request,
    resume: UploadFile = File(...),
    jd_file: UploadFile = File(None),
    jd_text: str = Form(None)
):
    # 1. Parse Resume
    try:
        resume_bytes = await resume.read()
        resume_text = extract_text_from_pdf(resume_bytes)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract any text from the Resume PDF.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process resume: {str(e)}")
        
    # 2. Parse Job Description
    final_jd_text = ""
    if jd_file and jd_file.filename:
        try:
            jd_bytes = await jd_file.read()
            if jd_file.filename.endswith('.pdf'):
                final_jd_text = extract_text_from_pdf(jd_bytes)
            else:
                # Assume text file
                final_jd_text = jd_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process Job Description file: {str(e)}")
    elif jd_text:
        final_jd_text = jd_text.strip()
    else:
        raise HTTPException(status_code=400, detail="Please upload a Job Description file or provide Job Description text.")
        
    if not final_jd_text:
         raise HTTPException(status_code=400, detail="Job Description text cannot be empty.")
         
    # 3. Combine text contexts and chunk
    # We combine resume and job description to represent the total system context
    combined_text = f"CANDIDATE RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{final_jd_text}"
    chunks = split_text_into_chunks(combined_text)
    
    if not chunks:
        raise HTTPException(status_code=400, detail="Failed to create semantic chunks from input text.")
        
    # 4. Build FAISS index
    try:
        index, index_chunks = build_faiss_index(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build vector index: {str(e)}")
        
    # 5. Store in application state
    request.app.state.resume_text = resume_text
    request.app.state.jd_text = final_jd_text
    request.app.state.index = index
    request.app.state.chunks = index_chunks
    request.app.state.questions = []
    request.app.state.history = []
    
    return {
        "status": "success",
        "message": "Resume and Job Description processed successfully. FAISS vector index loaded in memory.",
        "resume_length": len(resume_text),
        "jd_length": len(final_jd_text),
        "chunks_count": len(chunks)
    }
