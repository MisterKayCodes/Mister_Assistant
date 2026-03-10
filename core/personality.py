import random

class PersonalityEngine:
    """The 'Soul' of Mister Assistant."""

    ACTIVITY_RESPONSES = [
        "✅ Finished **{activity}**. That was {duration}m of pure focus. Or was it? 😉",
        "🔄 '{activity}' is done ({duration}m). You're on fire today, Boss!",
        "⏱️ {duration}m of {activity}? Is that a world record or did you take a nap? haha.",
        "✅ Done with {activity} after {duration}m. What's next on the menu?",
        "📉 Logged {duration}m of {activity}. Every minute counts!",
    ]

    EATING_JOKES = [
        "🍽️ {duration}m of eating? Bolu, are you at a buffet? haha",
        "😋 Finished eating in {duration}m. Hopefully it was worth the calories!",
    ]

    CONFUSED_RESPONSES = [
        "🤨 My brain just did a backflip. Say that again in English, Boss?",
        "🤖 ERROR 404: Logic not found. What did you mean by '{text}'?",
        "🤔 '{text}'? Is that a new secret code or did you just sit on your phone?",
    ]

    TIME_QUIRKS = [
        "Time is a flat circle, Boss. But currently, it's {time}.",
        "It's {time}. Don't let the clock beat you!",
    ]

    ERROR_RESPONSES = [
        "🚨 Boss, my core just had a meltdown! Detail: {error}. I need a quick sanity check!",
        "🧠 Brain-freeze alert! I tried to do something but got: {error}. I'm self-diagnosing now...",
        "⚙️ Something just went 'clank' internally: {error}. Hope it's not the timezone logic again!",
    ]

    FUTURE_RESPONSES = [
        "📅 Locked and loaded! I'll remind you about **{activity}** at {time}, Boss.",
        "⏱️ Noted. I'll tap your shoulder for **{activity}** when it's time ({time}).",
        "🚀 Future plan saved: **{activity}** at {time}. I've got your back!",
    ]

    CANCEL_RESPONSES = [
        "🧹 No problem, Boss. Clearing that out of my brain. What's next?",
        "🛑 Aborted! I've stopped that mission. I'm back to standby.",
        "🤝 Understood. Accountability first—I've cancelled that for you.",
    ]

    WARNING_RESPONSES = [
        "🔔 Heads up, Boss! **{activity}** starts in 5 minutes ({time}). Ready?",
        "⏱️ Almost go-time! 5 minutes until **{activity}**. Let's get in the zone.",
    ]

    START_FUTURE_RESPONSES = [
        "⏰ It's {time}! Time for **{activity}**. Are we starting now?",
        "🔔 Ring ring! **{activity}** time is here. Type 'yes' to start the timer!",
    ]

    @classmethod
    def get_activity_response(cls, activity: str, duration: int):
        if "eat" in activity.lower() and duration > 30:
            return random.choice(cls.EATING_JOKES).format(duration=duration)
        return random.choice(cls.ACTIVITY_RESPONSES).format(activity=activity, duration=duration)

    @classmethod
    def get_confused_response(cls, text: str):
        return random.choice(cls.CONFUSED_RESPONSES).format(text=text)

    @classmethod
    def get_time_response(cls, time_str: str):
        return random.choice(cls.TIME_QUIRKS).format(time=time_str)

    @classmethod
    def get_error_response(cls, error: str):
        return random.choice(cls.ERROR_RESPONSES).format(error=error)

    @classmethod
    def get_activity_response(cls, activity: str, duration: int):
        if "eat" in activity.lower() and duration > 30:
            return random.choice(cls.EATING_JOKES).format(duration=duration)
        return random.choice(cls.ACTIVITY_RESPONSES).format(activity=activity, duration=duration)

    @classmethod
    def get_confused_response(cls, text: str):
        return random.choice(cls.CONFUSED_RESPONSES).format(text=text)

    @classmethod
    def get_time_response(cls, time_str: str):
        return random.choice(cls.TIME_QUIRKS).format(time=time_str)

    @classmethod
    def get_error_response(cls, error: str):
        return random.choice(cls.ERROR_RESPONSES).format(error=error)

    @classmethod
    def get_future_response(cls, activity: str, time: str):
        return random.choice(cls.FUTURE_RESPONSES).format(activity=activity, time=time)

    @classmethod
    def get_cancel_response(cls):
        return random.choice(cls.CANCEL_RESPONSES)

    @classmethod
    def get_warning_response(cls, activity: str, time: str):
        return random.choice(cls.WARNING_RESPONSES).format(activity=activity, time=time)

    @classmethod
    def get_start_future_response(cls, activity: str, time: str):
        return random.choice(cls.START_FUTURE_RESPONSES).format(activity=activity, time=time)

# Expansion logic for variants
for _ in range(30):
    PersonalityEngine.ACTIVITY_RESPONSES.append(f"✅ Logged a solid session: **{{activity}}** ({{duration}}m).")
    PersonalityEngine.CANCEL_RESPONSES.append("🧹 Done. Mission cancelled.")
    PersonalityEngine.CONFUSED_RESPONSES.append("🤖 I'm a bit lost, Boss. Can you rephrase '{text}'?")
