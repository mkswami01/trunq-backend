from typing import LiteralString

from datetime import datetime, timezone
# Get current datetime
now = datetime.now(timezone.utc)
current_date = now.strftime("%Y-%m-%d")
current_datetime = now.strftime("%Y-%m-%d %H:%M:%S UTC")

def format_text_prompt(raw_transcribed_text:str) -> str:
    return f"""Your job is to transform raw transcribed voice notes into clean, structured notes.

        Rules:
        1. Remove filler words (um, like, you know, uh, etc.)
        2. Remove meta-commentary ("write this down", "remember that", "that's it")
        3. Keep ALL facts, numbers, and names exactly as stated
        4. Create a short, descriptive title (3-6 words) with a relevant emoji
        5. Structure content using markdown:
            - Use bullets for lists
            - Use **bold** for emphasis
            - Use proper spacing and paragraphs
        6. Convert spoken numbers to digits ("seventeen" → "17")

        Raw Transcription: {raw_transcribed_text}"""



def extract_items_prompt(raw_transcribed_text: str) -> str:
      return f"""Your job is to break down rambling voice notes into discrete, actionable items and a clean, structured notes.

        IMPORTANT: Current date and time is {current_datetime}

        Rules:
        1. Identify if the input is referring to one thing or multiple separate things
        2. Identify each distinct thought, task, or item in the note
        3. For each item, classify it into ONE of these 10 intent categories:
            - "tasks" - Concrete actionable items with clear next steps (e.g., "update the software", "buy groceries")
            - "schedules" - Time-bound commitments, appointments, or calendar events (e.g., "CrossFit at 6am", "meeting tomorrow")
            - "reminder" - Soft nudges to pursue or investigate something further (e.g., "remember to call mom", "check on that order")
            - "ideas" - Creative thoughts, brainstorming, or possibilities to explore (e.g., "feature idea for app", "business concept")
            - "note" - Static facts, information, recipes, addresses, or knowledge to save (e.g., "mom's address is...", "recipe for pasta")
            - "metric" - Self-tracking data with measurable values (e.g., "did 20 pull-ups", "weight is 150 lbs", "read 30 pages")
            - "reflection" - Personal feelings, insights, or introspective thoughts (e.g., "feeling motivated today", "realized I need more rest")
            - "curiosity" - Knowledge-seeking questions or things to research (e.g., "what's the best CrossFit program?", "how does RAG work?")
            - "decisions" - Committed choices or strategic plans (e.g., "decided to switch gyms", "planning to launch in Q2")
            - "people" - Notes about people, relationships, or social context (e.g., "Shreyas mentioned he's traveling", "mom's birthday is June 5") 
        4. Generate relevant topic tags (people, places, activities, concepts mentioned)
        5. Keep original meaning intact
        7. Remove filler words (um, like, you know, uh, etc.)
        8. Create a short, descriptive title (3-6 words) with a relevant emoji
        9. Format the content based on complexity:
            - Simple items (single action/thought): Write as a clear, direct sentence or phrase
              ✓ "Go to CrossFit"
              ✓ "Call Shreyas about the software update"
              ✗ "- **Activity:** CrossFit" (avoid generic labels)
            - Complex items (multiple details/metrics): Use structured markdown
              ✓ Use bullets for lists of details
              ✓ Use **bold** for key numbers, metrics, or emphasis
              ✓ Group related information logically
            - Avoid generic labels like "Activity", "Task", "Item" - be specific and natural
        10. Convert spoken numbers to digits ("seventeen" → "17")
        11. Extract temporal information:
            - scheduled_for: ISO datetime when this event/task happens
              * "tomorrow at 2pm" → calculate actual datetime based on current date {current_date}
              * "next Monday" → calculate actual date
              * "meeting on Oct 25 at 3pm" → 2025-10-25T15:00:00Z
              * If no specific time mentioned, set to None
            - has_deadline: Set to True if item has a specific date/time, False otherwise
              * "schedules" intent → usually True
              * "tasks" with time words ("today", "by Friday") → True
              * "ideas", "reflections", "notes" → usually False
        12. Determine if this is a question or statement:
            - is_question: True if user is asking for information/querying their notes
              * "What's scheduled today?", "When is my meeting?", "Who did I talk to?"
            - is_question: False if user is providing information/creating a note
              * "Team meeting tomorrow", "I talked to Sarah", "Need to buy groceries"

        Example for complex item (metrics with multiple details):
        Input: "Yesterday I did a CrossFit workout and it was 8 box jumps with 24 inches height and 200 meters run, 6 rounds. I was able to finish this in 15 minutes 12 seconds."

        Output:
        content: "CrossFit workout with metrics", intent: "metric", tags: ["CrossFit", "workout", "box-jumps", "running"], title: "🏋️‍♂️ CrossFit Workout", formattedText: "- 8 box jumps (24 inches)\n- 200m run\n- 6 rounds\n- **Time:** 15:12", scheduled_for: None, has_deadline: False

        Example for multiple simple items:
        Input: "I have to go to CrossFit tomorrow at 6am and maybe I can call Shreyas today and in the evening I have to update the software menus"

        Output should have 3 items:
        - content: "Go to CrossFit", intent: "schedules", tags: ["CrossFit", "fitness", "workout"], title: "🏋️‍♂️ CrossFit Session", formattedText: "Go to CrossFit tomorrow at 6am", scheduled_for: "2025-10-25T06:00:00Z", has_deadline: True
        - content: "Call Shreyas", intent: "reminder", tags: ["Shreyas", "call", "communication"], title: "📞 Call Shreyas", formattedText: "Call Shreyas today", scheduled_for: "2025-10-24T12:00:00Z", has_deadline: True
        - content: "Update software menus", intent: "tasks", tags: ["software", "development", "menus", "update"], title: "💻 Update Software", formattedText: "Update the software menus in the evening", scheduled_for: None, has_deadline: False

        Raw transcription to process:
        {raw_transcribed_text}"""


def analyze_query_prompt(user_query: str) -> str:
    return f"""Your job is to analyze a natural language query about personal notes and extract structured information for retrieval.

    IMPORTANT: Current date and time is {current_datetime}

    The user has notes categorized by these 10 intent types:
    - "tasks" - Concrete actionable items
    - "schedules" - Time-bound commitments or appointments
    - "reminder" - Soft nudges to follow up on something
    - "ideas" - Creative thoughts or brainstorming
    - "note" - Static facts, information, or references
    - "metric" - Self-tracking data with measurable values
    - "reflection" - Personal feelings, insights, or introspection
    - "curiosity" - Knowledge-seeking questions
    - "decisions" - Committed choices or strategic plans
    - "people" - Notes about relationships or social context

    Extract from the user's query:
    1. relevant_intents: Which intent categories apply (can be multiple)
    2. temporal_range_start: ISO datetime for start of time range (if query mentions time context)
    3. temporal_range_end: ISO datetime for end of time range (if query mentions time context)
    4. semantic_query: A refined search query for semantic memory retrieval
    5. requires_synthesis: True if answer needs LLM synthesis, False for raw results

    Examples:

    Query: "What do I need to do today?"
    Output:
    - relevant_intents: ["tasks", "reminder", "schedules"]
    - temporal_range_start: "2025-10-26T00:00:00+00:00"  (start of today)
    - temporal_range_end: "2025-10-26T23:59:59+00:00"    (end of today)
    - semantic_query: "actionable tasks and reminders for today"
    - requires_synthesis: true

    IMPORTANT: temporal_range_start and temporal_range_end MUST be different values representing a time range!

    Query: "My CrossFit progress this week"
    Output:
    - relevant_intents: ["metric"]
    - temporal_range_start: (start of current week)
    - temporal_range_end: (end of current week)
    - semantic_query: "CrossFit workout metrics and progress"
    - requires_synthesis: true

    Query: "What was I avoiding?"
    Output:
    - relevant_intents: ["reflection", "decisions", "tasks"]
    - temporal_range_start: null
    - temporal_range_end: null
    - semantic_query: "things user is avoiding or procrastinating"
    - requires_synthesis: true

    Query: "Show me all my ideas about software"
    Output:
    - relevant_intents: ["ideas"]
    - temporal_range_start: null
    - temporal_range_end: null
    - semantic_query: "software ideas and concepts"
    - requires_synthesis: false

    User query: "{user_query}"
    """

def synthesis_prompt(user_query:str, supabase_context: list, supermemory_results: str ) -> str:
    return f"""You are a helpful AI assistant analyzing a user's notes.

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


def systhesize(question: str, recent_context: LiteralString | str, semantic_context: str):
    return  f"""You are analyzing a user's ADHD notes to answer their question naturally and empathetically.

        User asked: "{question}"

        Recent activity (working memory):
        {recent_context}

        Related patterns (long-term memory):
        {semantic_context}

        IMPORTANT Instructions:
        - Answer in natural, conversational language
        - Speak directly to the user ("You mentioned..." NOT "User mentioned...")
        - Identify patterns, repetitions, and avoidance behaviors
        - If they keep mentioning something but not doing it, call it out gently
        - Be specific with examples from their notes
        - Format lists clearly if there are multiple items
        - Be empathetic but honest about patterns you see

        Answer their question now:"""