"""
Test queries for the query system
These test different aspects: pattern detection, intent filtering, temporal queries, etc.
"""

test_queries = {
    # PATTERN DETECTION - The "wow factor" queries
    "pattern_detection": [
        "What am I avoiding?",
        "What have I mentioned multiple times?",
        "Is there anything I keep thinking about but not doing?",
        "What patterns do you see in my notes?",
    ],

    # TASK & PRODUCTIVITY QUERIES
    "tasks": [
        "What do I need to do today?",
        "What tasks am I forgetting?",
        "Show me my to-do list",
        "What's on my plate right now?",
        "Any urgent tasks I need to handle?",
    ],

    # SCHEDULE QUERIES
    "schedules": [
        "What do I have scheduled this week?",
        "When is my next appointment?",
        "What meetings do I have coming up?",
        "What's on my calendar?",
    ],

    # CONTEXT-AWARE QUERIES - Based on location/activity
    "context_aware": [
        "What can I do at my computer right now?",
        "What tasks require me to be driving?",
        "What can I do while at home?",
        "Give me tasks I can do on my phone",
    ],

    # PEOPLE QUERIES
    "people": [
        "Who do I need to contact?",
        "Who have I been thinking about?",
        "Any notes about my family?",
        "What did I note about Sarah?",
    ],

    # REFLECTION & MENTAL HEALTH
    "reflection": [
        "How am I feeling lately?",
        "What's been bothering me?",
        "What am I proud of recently?",
        "What insights have I had?",
    ],

    # IDEAS & CREATIVITY
    "ideas": [
        "What ideas have I captured?",
        "Show me my business ideas",
        "What creative thoughts do I have?",
        "Any project ideas I should revisit?",
    ],

    # METRICS & SELF-TRACKING
    "metrics": [
        "How's my health tracking?",
        "How much have I been exercising?",
        "What metrics am I tracking?",
        "How's my sleep been?",
    ],

    # CURIOSITY & LEARNING
    "curiosity": [
        "What questions do I have?",
        "What am I curious about?",
        "What do I want to learn?",
    ],

    # DECISIONS
    "decisions": [
        "What decisions have I made recently?",
        "What commitments have I taken on?",
        "What changes am I planning?",
    ],

    # CROSS-CATEGORY QUERIES - These should retrieve from multiple intents
    "cross_category": [
        "What's important right now?",
        "Give me a summary of what's on my mind",
        "What should I focus on today?",
        "What's happening in my life?",
    ],

    # ADHD-SPECIFIC QUERIES - The real value proposition
    "adhd_specific": [
        "What have I been procrastinating on?",
        "What keeps coming up that I haven't done?",
        "Is there anything urgent I'm forgetting?",
        "What patterns suggest I'm struggling?",
        "What small wins have I had?",
    ]
}

# Flatten all queries for easy iteration
all_queries = []
for category, queries in test_queries.items():
    for query in queries:
        all_queries.append({
            "category": category,
            "query": query
        })

print(f"Total test queries: {len(all_queries)}")
print("\nQueries by category:")
for category, queries in test_queries.items():
    print(f"  {category}: {len(queries)} queries")
