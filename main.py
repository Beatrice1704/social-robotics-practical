from autobahn.twisted.component import Component, run 
from twisted.internet.defer import inlineCallbacks 
from autobahn.twisted.util import sleep  
from google import genai

from utils.parsing import *
from utils.prompts import *


GEMINI_API_KEY = "INSERT YOUR KEY HERE"
client = genai.Client(api_key=GEMINI_API_KEY)


def gemini_generate_text(prompt: str, model: str = "gemini-2.5-flash") -> str:
    resp = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return (resp.text or "").strip()


@inlineCallbacks
def say(session, stt, text):
    """
    Robot speaks safely:
    - disable STT (so it doesn't hear itself) (! not implemented)
    - speak using TTS 
    - small pause after speaking (! not implemented)
    """
    yield stt.before_robot_speaks(text)
    yield session.call("rie.dialogue.say", text=text)
    yield stt.after_robot_speaks()


@inlineCallbacks
def director_round(session, stt):
    # welcome
    yield say(session, stt, UTT_WELCOME)
    # fixed instruction
    yield say(session, stt, UTT_RULES)

    # Gemini
    raw = gemini_generate_text(build_director_prompt())
    secret, clue = parse_director(raw)

    if not secret or not clue:
        yield say(session, stt, "I had trouble choosing a word.")
        return

    # speak clue
    yield say(session, stt, clue)

    # listen (! not implemented)
    user_text = yield stt.listen(timeout_s=8.0)

    if not user_text:
        yield say(session, stt, UTT_DIDNT_CATCH)
        return

    # question vs guess
    if is_question(user_text):
        # Ask Gemini to answer without revealing the secret
        q_prompt = build_director_answer_prompt(secret=secret, clue=clue, question=user_text)
        a_raw = gemini_generate_text(q_prompt)

        m = re.search(r"ANSWER:\s*(.+)", a_raw)
        answer = m.group(1).strip()

        # Speak the answer
        yield say(session, stt, answer)

        return

    # Otherwise treat as a guess
    if user_text.lower().strip() == secret.lower():
        yield say(session, stt, UTT_CORRECT)
    else:
        yield say(session, stt, UTT_NOT_CORRECT)


@inlineCallbacks  
def main(session, details):  
    #yield session.call("rie.dialogue.say",  
    #text="Hello, I am successfully connected!")  
    #session.leave() # Close the connection with the robot  

# Create wamp connection  
#wamp = Component(  
    transports=[{  
        "url": "ws://wamp.robotsindeklas.nl",  
        "serializers": ["msgpack"]  
    }],  
    realm="ENTER YOUR REALM HERE",  
#)  
#wamp.on_join(main)  

if __name__ == "__main__":  
    #run([wamp]) 

    # CHECK DIRECTOR PROMPT
    print(gemini_generate_text(build_director_prompt()))

    # CHECK MATCHER PROMPT
    print(gemini_generate_text(build_matcher_prompt("It is an animal that lives in the sea")))