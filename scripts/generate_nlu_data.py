import csv
import itertools
import os
import random

# Core directories
TRAINING_DIR = os.path.join("data", "training")
os.makedirs(TRAINING_DIR, exist_ok=True)
DATASET_PATH = os.path.join(TRAINING_DIR, "intent_dataset.csv")

# Intent definitions
INTENTS = {
    "start_activity": [
        "starting {activity}",
        "begin {activity}",
        "im going to start {activity}",
        "about to do some {activity}",
        "time for {activity}",
        "heading to {activity}",
        "gonna {activity}"
    ],
    "end_activity": [
        "done",
        "finished",
        "im done",
        "stopped",
        "just finished",
        "all done",
        "im finished",
        "wrapping up",
        "that's it"
    ],
    "transition_activity": [
        "now {activity}",
        "shifting to {activity}",
        "moving to {activity}",
        "changing to {activity}",
        "gonna go do {activity} now",
        "im doing {activity} now instead",
        "switching to {activity}"
    ],
    "log_spending": [
        "spent {amount} on {category}",
        "paid {amount} for {category}",
        "bought {category} for {amount} naira",
        "dropped {amount} bucks on {category}",
        "got {category} for {amount}",
        "cost me {amount} to get {category}",
        "just spent {amount} for {category}",
        "spent {amount} NGN on {category}",
        "{amount} on {category}",
        "paid {amount} bucks for {category}",
        "bought {category} for ₦{amount}",
        "just paid ₦{amount} for {category}",
        "spent {amount}naira on {category}"
    ],
    "get_summary": [
        "summary",
        "show me my summary",
        "daily summary",
        "how did I do today",
        "what have I done today",
        "give me a report",
        "/summary",
        "report"
    ]
}

# Variable pools
ACTIVITIES = ["coding", "deep work", "reading", "gym", "workout", "lunch", "dinner", "meeting", "emails", "chores", "driving", "meditation"]
AMOUNTS = ["500", "1000", "5k", "10000", "50", "2.5k", "150", "8000", "1m", "200.50", "45"]
CATEGORIES = ["food", "gas", "uber", "dinner", "lunch", "coffee", "groceries", "subscription", "bills", "airtime", "data", "drinks"]

def generate_dataset():
    generated_data = []

    # Generate permutations
    for intent, templates in INTENTS.items():
        for template in templates:
            if "{activity}" in template:
                for activity in ACTIVITIES:
                    text = template.replace("{activity}", activity)
                    generated_data.append((text, intent))
            elif "{amount}" in template and "{category}" in template:
                for amount in AMOUNTS:
                    for category in CATEGORIES:
                        text = template.replace("{amount}", amount).replace("{category}", category)
                        generated_data.append((text, intent))
            else:
                generated_data.append((template, intent))

    # Add some noise/gibberish so the classifier handles low confidence well (mapped to a safe intent or it will just be low probability anyway, but let's give it an 'unknown' intent for now maybe? Actually, just let it output low prob for these. For now, we won't train on unknown. It will just predict an intent with < 0.75 confidence. But let's add some chit-chat mapping to 'idle_chat' just in case)
    IDLE_CHAT = [
        "hello", "hi", "how are you", "what's up", "the weather is nice",
        "who are you", "good morning", "good night", "thanks", "ok cool",
        "that's great", "I am tired", "lol", "haha", "yes", "no", "maybe"
    ]
    for text in IDLE_CHAT:
        generated_data.append((text, "idle_chat"))

    # Add variations without proper spacing
    generated_data.extend([
        ("spending500 on foo", "log_spending"),
        ("start gym", "start_activity"),
        ("nowlunch", "transition_activity"),
    ])

    # Shuffle dataset
    random.shuffle(generated_data)

    print(f"Generated {len(generated_data)} samples.")
    
    with open(DATASET_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "intent"])
        writer.writerows(generated_data)
    
    print(f"Dataset saved to {DATASET_PATH}")

if __name__ == "__main__":
    generate_dataset()
