from autobahn.twisted.component import Component, run 
from twisted.internet.defer import inlineCallbacks 
from autobahn.twisted.util import sleep  
from google import genai

from utils.prompts import build_director_prompt
from utils.prompts import build_matcher_prompt


GEMINI_API_KEY = "INSERT YOUR KEY HERE"
client = genai.Client(api_key=GEMINI_API_KEY)

def gemini_generate_text(prompt: str, model: str = "gemini-2.5-flash") -> str:
    resp = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return (resp.text or "").strip()

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