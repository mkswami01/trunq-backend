from fastapi import HTTPException
from fastapi.routing import APIRouter
import supermemory

from app.services.voice_service import VoiceService
from app.services import supermemory_service
from app.services.query_service import QueryService


router = APIRouter()


@router.post("/add-note")
async def add_notes(text: str) -> dict:  # ✅ Fixed: returns dict not str
    try:
        voiceservice = VoiceService()
        supermemory = supermemory_service.SupermemoryService()
        extracted_data = voiceservice.extract_and_split(text)


        responses = []
        for item in extracted_data["items"]:  # ✅ Fixed: iterate over items
              result = await supermemory.add_document(item, "demo_user")  # ✅ Fixed: await
              responses.append(result)

        return {
            "status": "success",
            "items_created": len(responses),
            "items": responses
        }
    except Exception as e:
        print(f"Error adding note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_notes(q: str):
    try:
        supermemory = supermemory_service.SupermemoryService()
        return await supermemory.two_phrase_search("demo_user", q, limit=10)
    except Exception as e:
        print(f"Failed to fetch {e}")
        raise HTTPException(status_code=500, detail="failed to fetch")


@router.post("/chat-test")
async def chat_test(q: str):
    try:
        supermemory = supermemory_service.SupermemoryService()
        return supermemory._analyze_query(q)  # ✅ No await - not an async method
    except Exception as e:
        print(f"Failed to fetch {e}")
        raise HTTPException(status_code=500, detail=str(e))

        



        
    
