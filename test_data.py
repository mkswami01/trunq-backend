import requests
"""
Test data generator for text note ingestion
Creates 100 realistic ADHD-style notes across all 10 intent categories
"""

test_notes = [
    # TASKS (20 items)
    "Call mom about her birthday party next week",
    "Buy groceries - milk, eggs, bread, and coffee",
    "Email Sarah about the project deadline extension",
    "Schedule dentist appointment for cleaning",
    "Pay electricity bill before Friday",
    "Return Amazon package at post office",
    "Update resume with new job responsibilities",
    "Fix the leaky faucet in bathroom",
    "Renew car insurance policy",
    "Clean out garage this weekend",
    "Submit expense report for last month",
    "Book flight tickets for conference",
    "Call plumber about kitchen sink",
    "Download tax documents from bank",
    "Order new running shoes online",
    "Send birthday card to cousin",
    "Water the plants on balcony",
    "Backup phone photos to cloud",
    "Cancel unused gym membership",
    "Reply to client email about meeting",

    # SCHEDULES (15 items)
    "Team meeting tomorrow at 2pm with marketing",
    "CrossFit class on Wednesday at 6am",
    "Doctor appointment next Tuesday at 10:30am",
    "Coffee with James on Friday at Starbucks downtown",
    "Parent teacher conference on Monday 4pm",
    "Yoga class every Thursday evening at 7pm",
    "Flight to Austin on March 15th at 9am",
    "Lunch with Sarah next Wednesday at noon",
    "Dentist cleaning on January 20th at 3pm",
    "Conference call with London office at 5am tomorrow",
    "Kids soccer game Saturday at 9am",
    "Date night with partner Friday 7pm at Italian place",
    "Oil change appointment Tuesday morning 8am",
    "Quarterly review meeting with boss on 25th",
    "Concert tickets for next month on the 18th",

    # REMINDERS (10 items)
    "Don't forget to call mom, been meaning to for days",
    "Remember to take medication before bed",
    "Need to follow up with John about that thing",
    "Check in on the project status tomorrow",
    "Should probably text back Lisa",
    "Look into that course I wanted to take",
    "Need to review those documents soon",
    "Consider scheduling that meeting we discussed",
    "Think about calling the insurance company",
    "Maybe reach out to old colleague about opportunity",

    # IDEAS (12 items)
    "What if we built a feature that shows patterns in user behavior",
    "Maybe start a newsletter about productivity for ADHD folks",
    "App idea: calendar that understands energy levels throughout day",
    "Could write a blog post about my morning routine struggles",
    "Thinking about starting a side project with machine learning",
    "Recipe idea - combine Thai curry with Mexican flavors",
    "Business idea for ADHD coaching service online",
    "Book idea about navigating tech career with ADHD",
    "Maybe redesign the living room with minimalist aesthetic",
    "Podcast concept interviewing people about their productive failures",
    "Create a course teaching developers about accessible design",
    "YouTube channel showing behind the scenes of startup building",

    # NOTES (10 items)
    "Password for work VPN is stored in 1Password under office folder",
    "Mom's new address is 123 Oak Street, apartment 4B",
    "Favorite coffee shop downtown is called Blue Bottle on 5th",
    "Car license plate renewal code is XY789123",
    "WiFi password for home network is sunflower2024",
    "Doctor's office phone number is 555-0123",
    "Good Thai restaurant recommendation from Mike - Lotus Garden",
    "Plumber said to call back if leak continues, number 555-7890",
    "Favorite running route is around the lake, exactly 5 miles",
    "Book recommendation from podcast - Atomic Habits by James Clear",

    # METRICS (10 items)
    "Went to gym today, did 45 minutes cardio and weights",
    "Slept 6 hours last night, woke up 3 times",
    "Drank 4 cups of coffee today, probably too much",
    "Weight this morning was 165 pounds",
    "Meditated for 15 minutes using Headspace app",
    "Walked 8000 steps according to phone",
    "Spent 3 hours in deep work on the project",
    "Had 2 productive hours before first meeting",
    "Blood pressure reading was 120 over 80",
    "Completed 5 out of 7 planned tasks today",

    # REFLECTIONS (10 items)
    "Feeling overwhelmed with all the projects at work lately",
    "Really proud of how I handled that difficult conversation",
    "Been struggling with focus this week, might need to adjust meds",
    "Noticed I'm happier when I exercise in the morning",
    "Feeling anxious about the presentation next week",
    "Grateful for supportive friends during tough time",
    "Realized I work better in coffee shops than at home",
    "Been avoiding that project because it feels too big",
    "Feel like I'm finally getting better at saying no",
    "Wish I had more energy in afternoons",

    # CURIOSITY (5 items)
    "How does semantic search actually work under the hood?",
    "Why do some people need less sleep than others?",
    "What's the best way to learn a new programming language?",
    "How do successful people manage their time differently?",
    "Why is it so hard to build new habits?",

    # DECISIONS (4 items)
    "Decided to switch to remote work schedule starting next month",
    "Going to try the new ADHD medication doctor recommended",
    "Committed to waking up at 6am every day for 30 days",
    "Choosing to focus on health over career for next quarter",

    # PEOPLE (4 items)
    "Sarah mentioned she's looking for new job opportunities",
    "Mom said she might visit in spring",
    "John's daughter just started college studying engineering",
    "Talked to old friend Lisa, she moved to Portland",
]

# Verify we have 100 notes
print(f"Total test notes created: {len(test_notes)}")

# Print distribution by category
categories = {
    "tasks": 20,
    "schedules": 15,
    "reminders": 10,
    "ideas": 12,
    "notes": 10,
    "metrics": 10,
    "reflections": 10,
    "curiosity": 5,
    "decisions": 4,
    "people": 4
}

print("\nSending notes to API...")
for i, items in enumerate(test_notes, 1):
    response = requests.post(
        "http://localhost:8000/api/v1/note/add-note",
        params={"text": items}  # ✅ Fixed: use params not json
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ [{i}/100] Success - {items[:50]}...")
    else:
        print(f"❌ [{i}/100] Failed - {response.status_code}: {items[:50]}...")