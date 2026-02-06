from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from google import genai
from google.genai import types
import os
import re

# This demo is a very straightforward implementation of a text-based chatbot using google's
# generative AI, Gemini
# To use Gemini, you need to acquire a (free) key that you submit to your system environment.
# Learn more at https://ai.google.dev/gemini-api

# Setting the API KEY
#chatbot = genai.Client(api_key=os.environ["api"])

# GLOBAL VARIABLES

ROUND_DURATION_S = 60.0
MAX_MEMORY_TURNS = 8

# GEMINI SETUP

chatbot = genai.Client(api_key="api")

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
        print("ASR response: ",query)
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
    yield session.call("rie.dialogue.say", text=text)
    yield sleep(cooldown_s)
    robot_is_speaking = False

def build_controller_prompt(role: str, memory: list[str], user_text: str) -> str:
    """
    One prompt that controls the game turn.
    LLM decides what to do (ask question, make guess, give clue, confirm correct).
    CODE handles timeout and role switching.
    """
    mem = "\n".join(memory[-MAX_MEMORY_TURNS:]) if memory else "(none yet)"
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

    Conversation so far:
    {mem}

    Latest user utterance:
    {user_text}

    Output format (MUST follow exactly):
    SAY: <one short sentence to speak aloud>
    """

def parse_say(text: str) -> str:
    """
    Extract the SAY line.
    """
    m = re.search(r"SAY:\s*(.+)", text)
    return m.group(1).strip() if m else text.strip()

@inlineCallbacks
def main(session, details):
    global finish_dialogue, query, response
    # set language to English (use 'nl' for Dutch)
    yield session.call("rie.dialogue.config.language", lang="en")
    # let the robot stand up
    yield session.call("rom.optional.behavior.play",name="BlocklyStand")

    # prompt from the robot to the user to say something
    yield say(session, "Hi! Let's play With Other Words.")
    yield say(session, "Each round lasts one minute. We take turns: I explain, then I guess.")

    # setting up the automatic speech recognition
    # subscribes the asr function with the input stt stream
    yield session.subscribe(asr, "rie.dialogue.stt.stream")
    # calls the stream. From here, the robot prints each 'final' sentence
    yield session.call("rie.dialogue.stt.stream")

    # loop while user did not say exit or quit
    dialogue = True
    while dialogue:
        if (finish_dialogue):
            if query in exit_conditions:
                dialogue = False
                yield session.call("rie.dialogue.say","ok, I will leave you then")
                break
            elif (query != ""):
                response = chatbot.models.generate_content(
                    model="gemini-2.5-flash", contents=query)
                yield session.call("rie.dialogue.say", response.text)
            else:
                yield session.call("rie.dialogue.say", text="sorry, what did you say?")
            finish_dialogue = False
            query = ""

    # before leaving the program, we need to close the STT stream
    yield session.call("rie.dialogue.stt.close")
    # and let the robot crouch
    # THIS IS IMPORTANT, as this will turn of the robot's motors and prevent them from overheating
    # Always and your program with this
    yield session.call("rom.optional.behavior.play",name="BlocklyCrouch")
    session.leave()

wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.69846cbd8e17491bb13c9abb",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])

