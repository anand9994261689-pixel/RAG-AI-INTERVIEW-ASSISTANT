import os
import subprocess

# Install reportlab to quickly write a valid PDF file
try:
    import reportlab
except ImportError:
    print("Installing reportlab to generate test PDF...")
    subprocess.check_call(["pip", "install", "reportlab"])

from reportlab.pdfgen import canvas

def create_files():
    resume_path = "c:/Users/anand/OneDrive/Desktop/rag/resume.pdf"
    jd_path = "c:/Users/anand/OneDrive/Desktop/rag/jd.txt"
    
    # Generate Resume PDF
    print(f"Generating dummy Resume PDF at {resume_path}...")
    c = canvas.Canvas(resume_path)
    c.drawString(100, 750, "ANAND KUMAR")
    c.drawString(100, 735, "Email: anand@example.com | Exp: 3 Years")
    c.drawString(100, 710, "SKILLS:")
    c.drawString(120, 695, "Python, FastAPI, Streamlit, FAISS, Sentence Transformers")
    c.drawString(120, 680, "AWS (EC2, S3), PostgreSQL, Docker, Git")
    c.drawString(100, 650, "EXPERIENCE:")
    c.drawString(120, 635, "Full Stack AI Engineer at Tech Corp (2023 - Present)")
    c.drawString(120, 620, "- Built RAG-based AI Mock Interview platforms using FastAPI.")
    c.drawString(120, 605, "- Developed user-interactive tools with Streamlit dashboards.")
    c.drawString(120, 590, "- Designed vector storage models using FAISS for low-latency retrieval.")
    c.save()
    
    # Generate JD text
    print(f"Generating dummy JD text at {jd_path}...")
    with open(jd_path, "w", encoding="utf-8") as f:
        f.write("""
JOB DESCRIPTION: Senior Python / AI Engineer
Location: Remote
Skills Needed:
- Python, FastAPI
- Build responsive Streamlit dashboards
- Experience with vector databases (FAISS, Chroma)
- Integration of LLM services (Gemini, OpenAI)
- Experience deploying to AWS (scalable architectures)
""")
    print("Test files created successfully!")

if __name__ == "__main__":
    create_files()
