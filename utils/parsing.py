import re

def parse_director(text: str):
    """
    Expected format:
    SECRET: <word>
    CLUE: <clue>
    Returns (secret, clue) or (None, None) if parsing fails.
    """
    secret = re.search(r"SECRET:\s*(.+)", text)
    clue = re.search(r"CLUE:\s*(.+)", text)
    if not secret or not clue:
        return None, None
    return secret.group(1).strip(), clue.group(1).strip()

def parse_matcher(text: str):
    """
    Expected format:
    TYPE: GUESS or QUESTION
    TEXT: <content>
    Returns (type, text) or (None, None) if parsing fails.
    """
    typ = re.search(r"TYPE:\s*(GUESS|QUESTION)", text, re.I)
    msg = re.search(r"TEXT:\s*(.+)", text)
    if not typ or not msg:
        return None, None
    return typ.group(1).upper(), msg.group(1).strip()


def is_question(user_text: str) -> bool:
    t = user_text.strip().lower()
    if not t:
        return False
    if t.endswith("?"):
        return True
    question_starters = ("is ", "are ", "can ", "do ", "does ", "did ", "what ", "where ", "how ", "when ", "why ")
    return t.startswith(question_starters)