
from typing import Literal


class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class VoiceRepository:

    def __init__(self, supabase_client):
        self.supabase_client = supabase_client

    def upload_audio_file(self, filename: str, content:bytes) -> str:
        
        response =self.supabase_client.storage.from_("voice-recordings").upload(filename, content)

        # Get public URL (not full_path!)
        public_url = self.supabase_client.storage.from_("voice-recordings").get_public_url(response.path)
        
        return public_url

    def create_voice_note(self, audio_filename: str, audio_url:str) -> dict:
        try:
            """Insert DB record, return created row. No business logic."""
            result = self.supabase_client.table("user_files").insert({
                "audio_filename": audio_filename,
                "audio_url": audio_url,
                "category": "uncategorized"
            }).execute()
            return result.data[0]
        except Exception as e:
            raise DatabaseError(f"Error creating a new record: {str(e)}")


    def update_transcription(self, id, transcription, title, formatted_text) -> dict:
        try:
            response = self.supabase_client.table("user_files").update({"transcription": transcription, "title":title, "formatted_content":formatted_text}).eq("id", id).execute()
            return response.data[0]
        except Exception as e:
            raise DatabaseError(f"Error updating comment status: {str(e)}")   

    def get_all_notes(self):
        try:
            result = self.supabase_client.table("user_files").select("*").not_.is_("transcription", "null").execute()  # Use None for actual NULL values.eq("story_id", story_id).execute()
            return result.data 
        except Exception as e:
            raise DatabaseError(f"Error reading all the transcription {str(e)}")


    def search_notes(self, query:str):
        try:
            result = self.supabase_client.table("user_files").select("*").ilike("transcription", f"%{query}%").execute()  # Use None for actual NULL values.eq("story_id", story_id).execute()
            return result.data 
        except Exception as e:
            raise DatabaseError(f"Error reading all the transcription {str(e)}")


    def create_note_with_metadata(self, audio_file_name, audio_url, transcription, title, formatted_content, metadata) -> dict:
        try:
            """Insert DB record, return created row. No business logic."""
            result = self.supabase_client.table("user_files").insert({
                "audio_filename": audio_file_name,
                "audio_url": audio_url,
                "transcription": transcription,
                "title": title,
                "formatted_content":formatted_content,
                "metadata":metadata
            }).execute()

            return result.data[0]
        except Exception as e:
            raise DatabaseError(f"Error creating a new record: {str(e)}")

    def search_notes_by_metadata(self, relevant_intents:list[Literal]):
        try:
            result = self.supabase_client.table("user_files").select("*").in_("metadata->>intent", relevant_intents).execute()
            return result.data 
        except Exception as e:
            raise DatabaseError(f"Error reading all the transcription {str(e)}")