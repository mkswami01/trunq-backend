from datetime import datetime
import os

from fastapi import HTTPException
import supermemory
from app.core.config import settings
from app.core.supabase_client import get_supabase
from app.repositories.voice_repository import VoiceRepository
from openai import OpenAI
from io import BytesIO

from app.models.response import NoteMetadata
from app.utilities import prompt
from app.services.supermemory_service import SupermemoryService

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB (Whisper API limit)
class VoiceService:
    def __init__(self):
        supabase = get_supabase() 
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.repository = VoiceRepository(supabase)
        self.superMemoryService = SupermemoryService()

    def timestamp_filename(self, file:str) -> str :
        name = file.replace(" ", "_")
        name_without_ext = os.path.splitext(name)[0].lower()
        ext = os.path.splitext(name)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{name_without_ext}_{timestamp}{ext}"
    
    async def upload_and_create(self, filename: str, content: bytes) -> dict:
        file_size = len(content)

        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size / 1024 / 1024:.2f}MB (max: {MAX_FILE_SIZE / 1024 / 1024}MB)")  


        unique_name = self.timestamp_filename(filename) # genenrate unique name 
        audio_url = self.repository.upload_audio_file(unique_name, content) # url for the audio
        raw_transcription = self.transcribe(content, unique_name) #raw transcription
        extracted_data = self.extract_and_split(raw_transcription) #extracted

        first_item = extracted_data["items"][0]
        if first_item["isQuestion"]:
           results = await self.query_supermemory(first_item["formattedText"])
           # Return transcription + results so frontend can show the question
           return {
               "transcription": raw_transcription,
               "query": first_item["formattedText"],
               "results": results
           }


        response = []

        
        # 4. Save MULTIPLE notes (one per item)
        for item in extracted_data["items"]:
            db_response = self.repository.create_note_with_metadata(
                    audio_file_name=unique_name,
                    audio_url=audio_url,
                    transcription=raw_transcription,
                    title=item["title"],
                    formatted_content=item["formattedText"],
                    metadata={
                        "intent": item["intent"],
                        "tags": item["tags"]
                    }
                )

            await self.superMemoryService.add_note_memory(db_response, "demo_user")
            
            response.append(db_response)
        # 3. Save to database
        return response
    

    def transcribe(self, audio_content: bytes, filename: str):
        audio_file = BytesIO(audio_content)
        audio_file.name = filename
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
        return transcription.text


    def extract_and_split(self, raw_transcript):
        
        if len(raw_transcript.strip()) < 5:
            raise ValueError("Transcription too short - please speak more clearly")
        extract_prompt = prompt.extract_items_prompt(raw_transcript)


        response = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "user", "content": extract_prompt}],
            response_format=NoteMetadata,
            temperature=0.3
        )
        parsed = response.choices[0].message.parsed

        return parsed.model_dump()

    def get_all_notes(self) -> list[dict]:
        return self.repository.get_all_notes()
        
    def search_notes(self, query) -> list[dict]:
        return self.repository.search_notes(query)


    async def query_supermemory(self, query):
        try:
            supermemory = SupermemoryService()
            return await supermemory.two_phrase_search("demo_user", query, limit=10)
        except Exception as e:
            print(f"Failed to fetch {e}")
            raise HTTPException(status_code=500, detail="failed to fetch")