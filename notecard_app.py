import os
import random

# Name of the text file where all notecards will be stored
FILE_NAME = "notecards.txt"

def create_notecard():
    """Prompt the user to create a new notecard and append it to the file."""
    question = input("Enter the question: ")
    answer = input("Enter the answer: ")
    with open(FILE_NAME, "a", encoding="utf-8") as file:
        file.write("[notecard]\n")
        file.write("[q] " + question + "\n")
        file.write("[a] " + answer + "\n")
        file.write("\n")  # Extra newline for clarity
    print("Notecard added successfully.\n")

def parse_notecards():
    """Read the file and parse all notecards into a list of dictionaries."""
    if not os.path.exists(FILE_NAME):
        print("Notecard file not found. Please create some notecards first.")
        return []
    
    with open(FILE_NAME, "r", encoding="utf-8") as file:
        lines = file.readlines()

    notecards = []
    current_card = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        if line.startswith("[notecard]"):
            # If there is an existing card, add it to the list
            if current_card:
                notecards.append(current_card)
                current_card = {}
        elif line.startswith("[q]"):
            current_card["question"] = line[3:].strip()
        elif line.startswith("[a]"):
            current_card["answer"] = line[3:].strip()
    
    # Add the final card if it exists
    if current_card:
        notecards.append(current_card)
    
    return notecards

def practice_notecards():
    """Load the notecards and allow the user to practice by flipping each card."""
    cards = parse_notecards()
    if not cards:
        print("No notecards available to practice. Please add some first.\n")
        return

    # Shuffle the cards for random order
    random.shuffle(cards)
    print("\nStarting practice session. Press Enter to flip each card.\n")

    for i, card in enumerate(cards, start=1):
        print(f"Card {i} of {len(cards)}")
        print("Question: " + card.get("question", "No question provided."))
        input("Press Enter to reveal the answer...")
        print("Answer: " + card.get("answer", "No answer provided."))
        print("-" * 40)
    print("Practice session complete.\n")

def main():
    """Main menu loop for the notecard application."""
    while True:
        print("\n--- Notecard Application ---")
        print("1. Create a notecard")
        print("2. Practice notecards")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            create_notecard()
        elif choice == "2":
            practice_notecards()
        elif choice == "3":
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
