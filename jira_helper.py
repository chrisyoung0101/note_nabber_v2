
import json
import os
from collections import defaultdict

print("""
────────────────────────────────────────────────────────────────────────────
📋 Jira Story Intake Helper (with Parent/Child Grouping)
────────────────────────────────────────────────────────────────────────────

This script helps you document and understand Jira stories by sprint. It now
tracks parent-child relationships so you can see stories grouped by parent.

🟢 Instructions:
- Enter sprint metadata.
- Enter each story with its parent ticket (if applicable).
- Use 'done' to finish each answer, or 'pause' to save and resume later.
────────────────────────────────────────────────────────────────────────────
""")

SESSION_FILE = "jira_story_progress.json"

# Resume session if applicable
if os.path.exists(SESSION_FILE):
    resume = input("A saved session was found. Resume previous session? (y/n): ").strip().lower()
    if resume == "y":
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            session_data = json.load(f)
        sprint_info = session_data["sprint_info"]
        stories = session_data["stories"]
        parent_questions = session_data.get("parent_questions", {})
    else:
        os.remove(SESSION_FILE)
        sprint_info = {}
        stories = []
        parent_questions = {}
else:
    sprint_info = {}
    stories = []
    parent_questions = {}

# Collect sprint-level info
if not sprint_info:
    sprint_info["name"] = input("Sprint Name (e.g. Sprint 18): ").strip()
    sprint_info["start_date"] = input("Sprint Start Date (YYYY-MM-DD): ").strip()
    sprint_info["end_date"] = input("Sprint End Date (YYYY-MM-DD): ").strip()

# Questions for each story
story_questions = [
    "What is the Jira ticket number (e.g. CAR-1234)?",
    "What is the title or short description of this story?",
    "What is the business goal or purpose?",
    "What are the key tasks or actions required?",
    "Are there any technical components or APIs involved?",
    "What is the expected outcome or deliverable?",
    "Are there any dependencies (other Jira tickets)?",
    "Are there any blockers or open questions?",
    "Any related documentation or links?"
]

# Parent questions (applied only once per unique parent)
parent_questions_list = [
    "What is the title or summary of the parent story?",
    "What is the high-level objective of this epic or parent ticket?"
]

while True:
    start = input("\nStart a new story? (y/n): ").strip().lower()
    if start != "y":
        break

    story = {}
    story["answers"] = {}

    parent = input("What is the parent ticket number for this story? (e.g. CAR-1000 or 'none'): ").strip()
    story["parent"] = parent.upper() if parent.lower() != "none" else "none"

    for q in story_questions:
        print(f"\n{q}\n(Type 'done' to skip, 'pause' to save and exit)")
        lines = []
        while True:
            line = input("> ").strip()
            if line.lower() == "pause":
                with open(SESSION_FILE, "w", encoding="utf-8") as f:
                    json.dump({"sprint_info": sprint_info, "stories": stories, "parent_questions": parent_questions}, f, indent=2)
                print("Session saved. You can resume later by running this script again.")
                exit(0)
            elif line.lower() == "done":
                break
            else:
                lines.append(line)
        story["answers"][q] = lines

    stories.append(story)

    # If this is a new parent and not 'none', ask parent-level questions
    if story["parent"] != "none" and story["parent"] not in parent_questions:
        print(f"\nAnswering questions for parent ticket: {story['parent']}")
        parent_questions[story["parent"]] = {}
        for q in parent_questions_list:
            print(f"\n{q}\n(Type 'done' to skip)")
            lines = []
            while True:
                line = input("> ").strip()
                if line.lower() == "done":
                    break
                else:
                    lines.append(line)
            parent_questions[story["parent"]][q] = lines

# Organize stories by parent
grouped = defaultdict(list)
for story in stories:
    grouped[story["parent"]].append(story)

# Format output
output = f"## Sprint: {sprint_info['name']}\nStart: {sprint_info['start_date']}\nEnd: {sprint_info['end_date']}\n"

for parent, children in grouped.items():
    output += f"\n---\n### Parent: {parent}\n"
    if parent != "none":
        for q, lines in parent_questions.get(parent, {}).items():
            output += f"- **{q}**\n"
            for line in lines:
                output += f"  - {line}\n"

    for i, story in enumerate(children, 1):
        output += f"\n**Child Story {i}**\n"
        for q, lines in story["answers"].items():
            output += f"- **{q}**\n"
            for line in lines:
                output += f"  - {line}\n"

# Save final output
filename = f"{sprint_info['name'].replace(' ', '_')}_Jira_Stories.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write(output)

if os.path.exists(SESSION_FILE):
    os.remove(SESSION_FILE)

print(f"\nDocumentation complete. Saved to: {filename}")
