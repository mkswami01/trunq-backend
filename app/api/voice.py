import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from app.core.supabase_client import get_supabase
import os
from datetime import datetime
from app.services.voice_service import VoiceService
from app.services.supermemory_service import SupermemoryService
from app.services.query_service import QueryService

router = APIRouter()

# Allowed audio formats
ALLOWED_EXTENSIONS = {".wav", ".m4a", ".mp3", ".webm", ".ogg", ".flac"}


def validate_audio_file(file: UploadFile) -> None:
    """Validate uploaded audio file format and size."""
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check content type
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an audio file"
        )
        


@router.post("/add-voice", response_model=dict)
async def add_voice_notes(audio: UploadFile = File(...)) -> dict:
    audio_bytes = await audio.read()
    voice_service = VoiceService()

    filename = f"{uuid.uuid4().hex[:5]}.wav" # temporary for the frontend integrations 

    try:
        result = await voice_service.upload_and_create(filename, audio_bytes)

        # Detect if this is a query response (has 'results' key)
        # or a push response (list of database notes)
        if isinstance(result, dict) and "results" in result:
            # Query response: {transcription, query, results: [...]}
            return {
                "notes_created": len(result["results"]),
                "notes": result["results"],
                "status": "retrieved",
                "transcription": result["transcription"],
                "query": result["query"]
            }
        else:
            # Push response: list of database notes
            return {
                "notes_created": len(result),
                "notes": result,
                "status": "pushed"
            }
    except ValueError as e:  # File size validation
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:  # Storage/DB errors
        print(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

@router.post("/upload", response_model=dict)
async def upload_voice_note(file: UploadFile = File(...)):
    """
    Upload a voice note for transcription and categorization.

    Accepts: .wav, .m4a, .mp3, .webm, .ogg, .flac (max 25MB)
    """
    # Validate file
    validate_audio_file(file)

    # Read file content
    content = await file.read()

    voice_service = VoiceService()

    try:
        result = await voice_service.upload_and_create(file.filename, content)
        # result is now a list of created notes (one per split item)
        return {
            "notes_created": len(result),
            "notes": result,
            "status": "uploaded"
        }
    except ValueError as e:  # File size validation
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:  # Storage/DB errors
        print(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.get("/notes", response_model=List[dict])
async def get_voice_notes():
    try:
        voice_service = VoiceService()
        return voice_service.get_all_notes()
    except Exception as e:  # Storage/DB errors
        print(f"Failed to fetch {e}")
        raise HTTPException(status_code=500, detail="failed to fetch")


@router.get("/search", response_model=List[dict])
async def search_notes(q:str):
    try:
        print(f"query is")
        voice_service = VoiceService()
        return voice_service.search_notes(q)
    except Exception as e:
        print(f"Failed to fetch {e}")
        raise HTTPException(status_code=500, detail="failed to fetch")

    
@router.post("/query")
async def query_memory(q:str):
    try:
        print(f"query  memory {q}")
        supermemory = SupermemoryService()
        return await supermemory.query_memory("demo_user", q, 5)
    except Exception as e:
        print(f"Failed to fetch {e}")
        raise HTTPException(status_code=500, detail="failed to fetch")

@router.post("/chat")
async def chat_query(q:str):
    try:
        print(f"chat {q}")
        query_service = QueryService()
        return await query_service.answer_query(q, "demo_user")
    except Exception as e:
        print(f"Failed to fetch {e}")
        raise HTTPException(status_code=500, detail="failed to fetch")


@router.get("/memories")
def get_memories():
    try:
        print("we are getting all the memories assocaited with user_demo_user")
        supermemory = SupermemoryService()
        return supermemory.check_user_memories("demo_user")
    except Exception as e:
        print(f"Failed to fetch {e}")
        raise HTTPException(status_code=500, detail="failed to fetch")

# @router.get("/notes/{note_id}", response_model=dict)
# async def get_voice_note(note_id: int, db: Session = Depends(get_db)):
#     """Get a specific voice note by ID."""
#     note = db.query(VoiceNote).filter(VoiceNote.id == note_id).first()

#     if not note:
#         raise HTTPException(status_code=404, detail="Voice note not found")

#     return {
#         "id": note.id,
#         "filename": note.audio_filename,
#         "audio_url": note.audio_url,
#         "transcription": note.transcription,
#         "category": note.category,
#         "ai_summary": note.ai_summary,
#         "extracted_date": note.extracted_date,
#         "created_at": note.created_at,
#     }
