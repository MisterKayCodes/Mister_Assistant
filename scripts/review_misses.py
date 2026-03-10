import os
import csv
import json

LOG_PATH = os.path.join("data", "logs", "uncertain_queries.log")
DATASET_PATH = os.path.join("data", "training", "intent_dataset.csv")

VALID_INTENTS = [
    "start_activity", "end_activity", "transition_activity",
    "log_spending", "get_summary", "idle_chat"
]

def review_misses():
    if not os.path.exists(LOG_PATH):
        print("No uncertain queries to review!")
        return

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        print("Log is empty. No queries to review.")
        return

    new_data = []
    remaining_lines = []

    print(f"Found {len(lines)} uncertain queries. Let's review them.\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        try:
            entry = json.loads(line)
            text = entry["text"]
            pred_intent = entry["predicted_intent"]
            conf = entry["confidence"]
        except json.JSONDecodeError:
            continue

        print(f"\n---")
        print(f"User said: '{text}'")
        print(f"Bot guessed: '{pred_intent}' (Conf: {conf:.2f})")
        print("Available Intents:")
        for idx, intent in enumerate(VALID_INTENTS):
            print(f"  {idx}: {intent}")
        print("  s: Skip (keep in log for later)")
        print("  d: Delete (ignore completely)")

        choice = input("\nEnter correct intent number (or s/d): ").strip()

        if choice.lower() == 's':
            remaining_lines.append(line + "\n")
            continue
        elif choice.lower() == 'd':
            continue
        
        try:
            intent_idx = int(choice)
            if 0 <= intent_idx < len(VALID_INTENTS):
                correct_intent = VALID_INTENTS[intent_idx]
                new_data.append((text, correct_intent))
                print(f"-> Learned: '{text}' is now '{correct_intent}'")
            else:
                print("Invalid number. Skipping.")
                remaining_lines.append(line + "\n")
        except ValueError:
            print("Invalid input. Skipping.")
            remaining_lines.append(line + "\n")

    # Append to dataset
    if new_data:
        os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
        with open(DATASET_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(new_data)
        print(f"\nAdded {len(new_data)} new examples to the dataset!")
        print("-> Remember to run `python scripts/train_nlu.py` to update the brain!")

    # Update log file
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.writelines(remaining_lines)

if __name__ == "__main__":
    review_misses()
