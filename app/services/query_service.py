from openai import OpenAI
from app.core.config import settings
from app.core.supabase_client import get_supabase
from app.services.supermemory_service import SupermemoryService
from app.models.response import QueryAnalysis
from app.utilities import prompt
from app.services.voice_service import VoiceService


class QueryService:
    def __init__(self):
        self.llm = OpenAI(api_key=settings.openai_api_key)
        self.supermemory = SupermemoryService()

    async def answer_query(self, user_query: str, user_id: str):
        """Main method: Analyze query, retrieve from both sources, synthesize answer"""

        try:
            query_analysis = self._analyze_query(user_query)

            print(f"Query analysis: \n {query_analysis}")
            supabase_reponse = self._query_supabase(query_analysis)


            supermemory_response = await self._query_supermemory(query_analysis, user_id)

            result = self._synthesize_answer(user_query, supabase_reponse, supermemory_response)
            return result
        except Exception as e:
            print(f"Error querying {e}")

    def _analyze_query(self, user_query: str) -> QueryAnalysis:
        """Use LLM to extract structured information from the query"""

        query_prompt = prompt.analyze_query_prompt(user_query)
        try:
            response = self.llm.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[{"role": "user", "content": query_prompt}],
                response_format=QueryAnalysis,
                temperature=0.3
            )

            return response.choices[0].message.parsed
        except Exception as e:
            print(f"Exception caught while analyzing query {e}")
            raise

    def _query_supabase(self, analysis: QueryAnalysis):
        """Query Supabase with structured filters"""
        try:
            voice_service = VoiceService()
            return voice_service.repository.search_notes_by_metadata(analysis.relevant_intents)
        except Exception as e:
            print(f"Error reading data from Supabase: {e}")
            return []  # Return empty list instead of None

    async def _query_supermemory(self, analysis: QueryAnalysis, user_id: str):
        """Query Supermemory with semantic search"""
        return await self.supermemory.query_memory(user_id, analysis.semantic_query)
       
    def _synthesize_answer(self, user_query: str, supabase_results: list, supermemory_results: str) -> str:
        # Build context from both sources
        supabase_context = "\n".join([
            f"- {item['title']}: {item['formatted_content']}"
            for item in supabase_results
        ])

        # Create synthesis prompt
        synthesis_prompt = f"""You are a helpful AI assistant analyzing a user's notes.

User asked: "{user_query}"

Structured notes from database:
{supabase_context}

Contextual memories:
{supermemory_results}

Based on both sources above, provide a clear, concise answer to the user's question.
- Combine information from both sources
- Deduplicate if the same item appears in both
- Use natural, conversational language
- If it's a task/reminder query, format as a numbered list
"""

        # Call LLM
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper model for synthesis
            messages=[{"role": "user", "content": synthesis_prompt}],
            temperature=0.5
        )

        return response.choices[0].message.content