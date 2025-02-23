# backend/app.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from transcription import transcribe_video

app = FastAPI()

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIRECTORY = "uploads"
TRANSCRIPTS_DIRECTORY = "transcripts"

os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(TRANSCRIPTS_DIRECTORY, exist_ok=True)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Run transcription
        transcript_file = transcribe_video(file_path, TRANSCRIPTS_DIRECTORY)
        
        return JSONResponse({
            "message": "Transcription complete.",
            "transcript_file": transcript_file
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/download/{filename}")
async def download_transcript(filename: str):
    file_path = os.path.join(TRANSCRIPTS_DIRECTORY, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='text/plain', filename=filename)
    return JSONResponse({"error": "File not found."}, status_code=404)
