from typing import Literal, Optional
from supermemory import Supermemory
from app.core.config import settings
import json

from app.models.response import QueryAnalysis
from datetime import datetime, timezone
from openai import OpenAI

from app.utilities.prompt import systhesize


class SupermemoryService:
    def __init__(self) -> None:
        self.client = Supermemory(api_key=settings.supermemory_api_key)

    async def add_note_memory(self, note_data: dict, user_id: str):
        """Add new document to user's memory (Supermemory will create memories from it)"""

        print(f" Pushing to supermemory {note_data}")

        payload = {
            "content": note_data["formatted_content"],
            "container_tag": f"{user_id}",
            "metadata": {
                "note_id": note_data["id"],
                "intent": note_data["metadata"]["intent"],
                "tags": note_data["metadata"]["tags"],
                "title": note_data["title"],
                "date": note_data["uploaded_at"]
            }
        }
        # Print nicely formatted JSON
        print("Payload being sent:\n", json.dumps(payload, indent=4))

        # Now call the API
        try:
            response = self.client.documents.add(**payload)
            print(f"Document added to Supermemory: {response}")
        except Exception as e:
            print(f"Error adding document: {e}")

    
    async def add_document(self, extracted_item: dict, user_id: str):
        """Add new document to user's memory (Supermemory will create memories from it)"""

        print(f" Pushing to supermemory {extracted_item}")

        # Build metadata - only include scheduled_for if it exists
        metadata = {
            "title": extracted_item["title"],
            "intent": extracted_item["intent"],
            "tags": extracted_item["tags"],
            "raw_text": extracted_item["content"],
            "date": datetime.now(timezone.utc).isoformat(),
            "has_deadline": extracted_item["has_deadline"]
        }

        # Only add scheduled_for if it's not None (Supermemory doesn't accept null values)
        if extracted_item["scheduled_for"]:
            metadata["scheduled_for"] = str(int(extracted_item["scheduled_for"].timestamp()))

        payload = {
            "content": extracted_item["formattedText"],
            "container_tag": f"{user_id}",
            "metadata": metadata
        }
        # Now call the API
        try:
            response = self.client.documents.add(**payload)
            print(f"Document added to Supermemory: {json.dumps(str(response), indent=4)}")
            return response
        except Exception as e:
            print(f"Error adding document: {e}")
            raise Exception(f"Failed to add document: {e}")
            

    async def query_memory(self, user_id: str, question: str, limit:int):

        print(f"the question is {question}")
        try:
            results = self.client.search.memories(
                q=question,
                container_tag=f"{user_id}",
                limit=limit
            )

            print(f"raw result is {results}")

            if results.results:
                context = "\n".join([r.memory for r in results.results])

                print(f"context is {context}")
                return f"Relevant memories about the user:\n{context}"
            return "No relevant memories found."
        except Exception as e:
            return f"Error searching memories: {e}"


    


    async def two_phrase_search(self, user_id: str, question: str, limit: int = 10):
        """
        Two-phase retrieval pattern inspired by customer support cookbook:
        1. Analyze query to get relevant intent categories
        2. Recent chronological memories (working memory) - filtered by intent
        3. Semantic search (long-term patterns)
        4. LLM synthesis for natural answers
        """

        # Step 1: Analyze query to extract relevant intents
        query_analysis = self._analyze_query(question)

        print(f"Query analysis - relevant intents: {query_analysis.relevant_intents}")
        print(f"Query analysis - temporal range: {query_analysis.temporal_range_start} to {query_analysis.temporal_range_end}")


        # Phase 1: Recent chronological memories (working memory) - filtered by intent
        # TODO(human): Build combined filters for intent + temporal range
        # Structure: {"AND": [{"OR": [intent filters]}, temporal_start filter, temporal_end filter]}
        # For now, passing empty dict to fetch all
        
        intent_condition = [
            {"filterType": "metadata", "key": "intent", "value": intent, "negate": False}
            for intent in query_analysis.relevant_intents
        ]

        filter ={"OR":intent_condition}

        if query_analysis.temporal_range_start and query_analysis.temporal_range_end:
            start_condition = {
                "filterType": "numeric",
                "key": "scheduled_for",
                "value": str(int(query_analysis.temporal_range_start.timestamp())),  # ISO string
                "numericOperator": ">",
                "negate": False
            }

            end_condition = {
                "filterType": "numeric",
                "key": "scheduled_for",
                "value": str(int(query_analysis.temporal_range_end.timestamp())),  # ISO string
                "numericOperator": "<",
                "negate": False
            }

            filter = {"AND": [
                            filter, 
                            start_condition, 
                            end_condition
                ]}

            latest_context = self.check_user_memories(user_id, filter, limit)

            print(f"latest memory is {latest_context}")
            results = []
            for memory in latest_context:
                results.append({
                    "text": memory.summary,  # or memory.title?
                    "intent": memory.metadata.get('intent'),
                    "tags": memory.metadata.get('tags', []),
                    "timestamp": memory.metadata.get('scheduled_for'),
                    "status": "retrieved"
                })

            return results      
        else:
            

            print(f"Semantic Search")
            semantic_context = self.semantic_search(user_id, question)
            results = []
            for memory_text in semantic_context:  # semantic_context is already a list of strings
                results.append({
                    "text": memory_text,  # Use the string directly
                    "intent": None,  # Semantic search doesn't include metadata
                    "tags": [],
                    "timestamp": None,
                    "status": "retrieved"
                })
            return results

            # return semantic_context
        
        # # # Phase 3: LLM Synthesis
        # llm = OpenAI(api_key=settings.openai_api_key)

        # synthesis_prompt = systhesize(question, latest_context, semantic_context)

        # response = llm.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[{"role": "user", "content": synthesis_prompt}],
        #     temperature=0.6
        # )

        # return response.choices[0].message.content
        

    def _analyze_query(self, user_query: str) -> QueryAnalysis:
        """Analyze query to extract relevant intents (copied from QueryService to avoid circular import)"""
        from app.utilities import prompt

        llm = OpenAI(api_key=settings.openai_api_key)
        query_prompt = prompt.analyze_query_prompt(user_query)

        try:
            response = llm.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[{"role": "user", "content": query_prompt}],
                response_format=QueryAnalysis,
                temperature=0.3
            )
            return response.choices[0].message.parsed
        except Exception as e:
            print(f"Exception caught while analyzing query: {e}")
            # Return default analysis if parsing fails
            return QueryAnalysis(
                relevant_intents=["tasks", "reminder", "schedules"],
                temporal_filter="none",
                semantic_query=user_query,
                requires_synthesis=True
            )

    def check_user_memories(self, user_id: str, filters: dict, limit: int = 10):

        try:
            # Filters should be a complete filter dict like {"OR": [...]} or {"AND": [...]}
            if not filters:
                print("No filters provided, fetching all memories")
                memory_list = self.client.memories.list(
                    container_tags=[f"{user_id}"],
                    limit=limit * 3
                )
            else:
                
                # IMPORTANT: Supermemory requires filters as JSON string
                filter_json = json.dumps(filters)
                print(f"Using filters: {filter_json}")
                memory_list = self.client.memories.list(
                    container_tags=[f"{user_id}"],
                    filters=filter_json,
                    limit=limit * 3
                )

            print(f"Found {len(memory_list.memories)} memories")

            # Debug: Check if any memories have scheduled_for
            if len(memory_list.memories) > 0:
                memories_with_scheduled = [
                    m for m in memory_list.memories
                    if hasattr(m, 'metadata') and m.metadata and 'scheduled_for' in m.metadata
                ]
                print(f"DEBUG: {len(memories_with_scheduled)} memories have scheduled_for field")

                return memory_list.memories

            return [];
        except Exception as error:
            print(f'Error: {error}')

    def semantic_search(self, user_id:str, question:str):
        # Phase 2: Semantic search (long-term patterns)
        semantic = self.client.search.memories(
            q=question,
            container_tag=f"{user_id}",
            limit=5
        )

        print(f"Semantic response is {semantic.results}")
        semantic_context = [r.memory for r in semantic.results] if semantic.results else []

        print(f"Semantic response is {semantic_context}")
        return semantic_context

