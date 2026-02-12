from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from twisted.internet import reactor
from google import genai
import re
from alpha_mini_rug import perform_movement

# This demo is a very straightforward implementation of a text-based chatbot using google's
# generative AI, Gemini
# To use Gemini, you need to acquire a (free) key that you submit to your system environment.
# Learn more at https://ai.google.dev/gemini-api

# Setting the API KEY
chatbot = genai.Client(api_key="api_key")

ROUND_DURATION_S = 60.0
robot_is_speaking = False
robot_is_director = True
memory: list[str] = []


def gemini_generate_text(prompt: str, model: str = "gemini-2.5-flash") -> str:
    resp = chatbot.models.generate_content(model=model, contents=prompt)
    return (resp.text or "").strip()

exit_conditions = (":q", "quit", "exit")

finish_dialogue = False
query = "hello"
response = "qqq"


def asr(frames):
    global finish_dialogue
    global query, robot_is_speaking

    if robot_is_speaking:
        return
    if frames["data"]["body"]["final"]:
        query = str(frames["data"]["body"]["text"]).strip()
        print("ASR response: ", query)
        finish_dialogue = True


@inlineCallbacks
def say(session, text: str, cooldown_s: float = 0.8):
    """
    For speaking safely:
    - block ASR while speaking to reduce self-speech pickup
    - cooldown to avoid capturing speech tail
    """
    global robot_is_speaking
    robot_is_speaking = True

    try:
        yield perform_movement(
            session,
            frames=[
                {"time": 400,  "data": {"body.head.pitch": 0.1}},
                {"time": 1200, "data": {"body.head.pitch": -0.1}},
                {"time": 2000, "data": {"body.head.pitch": 0.1}},
                {"time": 2400, "data": {"body.head.pitch": 0.0}},
            ],
            force=True,
        )
    except Exception:
        pass
    yield session.call("rie.dialogue.say", text=text)
    yield sleep(cooldown_s)
    robot_is_speaking = False


def build_controller_prompt(role: str, memory: list[
    str], user_text: str
) -> str:
    """
    One prompt that controls the game turn.
    LLM decides what to do (ask question, make guess, give clue,
    confirm correct).
    CODE handles timeout and role switching.
    """
    mem = "\n".join(memory) if memory else ""
    return f"""Context:
    You are a conversational assistant embedded in a small social robot.
    You are playing the WOW (With Other Words) spoken word game.


    Role:
    {role}

    Rules:
    - DIRECTOR: You secretly choose one common English word (single word). Do NOT reveal it.
    Give short hints (1 sentence). If the user asks questions, answer briefly without revealing.
    If the user guesses correctly, respond with a short success message.
    - MATCHER: The user has a secret word and describes it. Ask ONE short clarification question if unsure,
    otherwise make ONE guess. Keep it brief for speech.

    If the word has been guessed correctly (by either side), set output WORD_IS_GUESSED: yes, otherwise set it to no.

    Conversation so far:
    {mem}

    Latest user utterance:
    {user_text}

    Output format (MUST follow exactly):
    SAY: <one short sentence to speak aloud>
    WORD_IS_GUESSED: <yes/no>
    """


def memory_add(mem: list[str], who: str, text: str):
    if text.strip():
        mem.append(f"{who}: {text.strip()}")


def parse_say(text: str) -> str:
    """
    Extract the SAY line.
    """
    line = re.search(r"SAY:\s*(.+)", text)
    return line.group(1).strip() if line else text.strip()


def parse_word_is_guessed(text: str) -> bool:
    line = re.search(r"WORD_IS_GUESSED:\s*(yes|no)", text, re.IGNORECASE)
    return (line.group(1).lower() == "yes") if line else False


def update_query() -> str:
    global finish_dialogue, query
    text = query.strip()
    finish_dialogue = False
    query = ""
    t = text.strip().lower()
    t = re.sub(r"[^\w:]+$", "", t)
    return t


@inlineCallbacks
def main(session, details):
    global finish_dialogue, query, response
    global robot_is_director, robot_is_speaking, memory
    # set language to English (use 'nl' for Dutch)
    yield session.call("rie.dialogue.config.language", lang="en")
    # let the robot stand up
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    # setting up the automatic speech recognition
    # subscribes the asr function with the input stt stream
    yield session.subscribe(asr, "rie.dialogue.stt.stream")
    # calls the stream. From here, the robot prints each 'final' sentence
    yield session.call("rie.dialogue.stt.stream")

    # prompt from the robot to the user to say something
    yield say(session, "Hi! Let's play With Other Words.")
    yield say(session, "Each round lasts one minute")
    yield say(session, "Do you want to be the director or the matcher?")

    while not finish_dialogue:
        yield sleep(0.05)
    user_response = update_query()

    if "matcher" in user_response:
        robot_is_director = True
        yield say(session, "I will explain a word and you'll try to guess it")
        yield sleep(0.05)
    if "director" in user_response:
        robot_is_director = False
        yield say(
            session, "You have to explain a word and I'll try to guess it")
        yield sleep(0.05)

    # start round with clear memory and start timer
    memory.clear()
    round_start = reactor.seconds()

    # loop while user did not say exit or quit
    dialogue = True
    while dialogue:
        yield sleep(0.05)

        # if the round is longer than 60 sec, terminate round
        if reactor.seconds() - round_start >= ROUND_DURATION_S:
            yield say(session, "Time is up!")
            robot_is_director = not robot_is_director
            memory.clear()
            round_start = reactor.seconds()

        if finish_dialogue:
            user_response = update_query()

            if user_response in exit_conditions:
                yield say(session, "ok, I will leave you then")
                break

            if user_response != "":
                role = "DIRECTOR" if robot_is_director else "MATCHER"

                memory_add(memory, "USER", user_response)

                prompt = build_controller_prompt(role, memory, user_response)
                llm_response = gemini_generate_text(prompt)
                word_is_guessed = parse_word_is_guessed(llm_response)

                robot_response = parse_say(llm_response)
                yield say(session, robot_response)
                yield sleep(0.08)

                memory_add(memory, "ROBOT", robot_response)

                if word_is_guessed:
                    yield say(session, "Nice! Do you want to play another round")
                    yield sleep(0.08)

                    # wait for yes/no
                    while not finish_dialogue:
                        yield sleep(0.08)
                    ans = update_query()

                    if ans in ("yes", "yeah", "yep", "sure", "ok", "okay"):
                        robot_is_director = not robot_is_director  # swap roles
                        memory.clear()
                        round_start = reactor.seconds()
                        yield say(session, "Great! New round.")
                        yield sleep(0.05)
                        continue
                    else:
                        yield say(session, "Okay, goodbye!")
                        break
            else:
                yield say(session, "sorry, what did you say?")
                yield sleep(0.05)

    # before leaving the program, we need to close the STT stream
    yield session.call("rie.dialogue.stt.close")
    # and let the robot crouch
    # THIS IS IMPORTANT, as this will turn of the robot's motors
    # and prevent them from overheating
    # Always and your program with this
    yield session.call("rom.optional.behavior.play", name="BlocklyCrouch")
    session.leave()


wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.698d8be5946951d690d13ad6",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
