CONTEXT_BLOCK = """Context:
You are a conversational assistant embedded in a small social robot.
The robot is playing a spoken word-guessing game with a human user.
The style should be friendly, brief, and suitable for spoken interaction.
Keep responses short and easy to say aloud.
"""

DIRECTOR_INSTRUCTIONS_BLOCK = """Instructions (Director role):
You are the DIRECTOR in the WOW (With other words) game.
You secretly choose one common English word (single word).
You must NOT reveal the secret word to the human.
You give short, clear clues (1-2 sentences) to help the human guess the word.
If the user asks a question, answer it without revealing the word.
Always keep your clue short for speech.
"""

DIRECTOR_ADDITIONAL_INFO_BLOCK = """Additional information:
- Game is educational and pleasant; keep it engaging.
- Provide a clue that is not too hard.
- Output format MUST be exactly:
SECRET: <word>
CLUE: <short clue>
"""

MATCHER_INSTRUCTIONS_BLOCK = """Instructions (Matcher role):
You are the MATCHER in the WOW game.
The human is thinking of a secret word and describing it.
Your job is to guess the word.
If you are unsure, ask ONE short clarifying question.
Keep everything short and natural for spoken dialogue.
Output format MUST be exactly:
TYPE: GUESS or QUESTION
TEXT: <your guess or your question>
"""

def build_director_prompt() -> str:
    return CONTEXT_BLOCK + "\n" + DIRECTOR_INSTRUCTIONS_BLOCK + "\n" + DIRECTOR_ADDITIONAL_INFO_BLOCK

def build_matcher_prompt(user_description: str) -> str:
    return CONTEXT_BLOCK + "\n" + MATCHER_INSTRUCTIONS_BLOCK + "\nHuman description:\n" + user_description



# Assignment suggests fixed utterances for instructions and ending rounds 
UTT_WELCOME = "Hi! Let's play With Other Words. We'll take turns: I explain, then I guess."
UTT_RULES = "When I explain, try to guess the word. You can ask short questions."
UTT_YOUR_TURN_DESCRIBE = "Now it's your turn. Think of a word and describe it, without saying it."
UTT_ROUND_OVER = "Time is up for this round."
UTT_PLAY_AGAIN = "Do you want to play another round? Say yes or no."
UTT_GOODBYE = "Okay! Thanks for playing. Bye!"

# Simple confirmation utterances
UTT_DIDNT_CATCH = "Sorry, I didn't catch that. Please say it again."
UTT_CORRECT = "Yes! Correct!"
UTT_NOT_CORRECT = "Not yet. Try again."
