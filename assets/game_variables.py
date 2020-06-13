import random
import datetime
import time

games_names_short = ["hm"]
game_names = ["hangman"]
randwords = list()

class Variables:
    EXTRA = ""
    DEADLINE = 600 * 2
    eng_dict = None
    questions_dict = None

    amtPlayedGames = {game_names[i]: 0 for i in range(len(game_names))}
    history = list()

    SPLIT_EMOJI = "↔️"
    INC_EMOJI1 = "⬆️"
    INC_EMOJI2 = "⏫"
    STOP_EMOJI = "❌"
    BACK_EMOJI = "◀"
    NEXT_EMOJI = "➡️"

    DICT_ALPHABET = {
        'a': '🇦', 'b': '🇧', 'c': '🇨', 'd': '🇩', 'e': '🇪', 'f': '🇫', 'g': '🇬', 'h': '🇭',
        'i': '🇮', 'j': '🇯',
        'k': '🇰', 'l': '🇱', 'm': '🇲', 'n': '🇳', 'o': '🇴', 'p': '🇵', 'q': '🇶', 'r': '🇷',
        's': '🇸', 't': '🇹',
        'u': '🇺', 'v': '🇻', 'w': '🇼', 'x': '🇽', 'y': '🇾', 'z': '🇿'}  # letter: emoji

    NUMBERS = ["0️⃣","1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    REACTIONS_CONNECT4 = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]

    HANGMAN0 = ""

    HANGMAN1 = "  |\n" \
               "  |\n" \
               "  |\n" \
               "  |\n" \
               " _|_ _ _"

    HANGMAN2 = " _____\n" \
               " |\n" \
               " |\n" \
               " |\n" \
               " |\n" \
               "_|_ _ _"

    HANGMAN3 = " _____\n" \
               " |/\n" \
               " |\n" \
               " |\n" \
               " |\n" \
               "_|_ _ _"

    HANGMAN4 = " _____\n" \
               " |/  |\n" \
               " |\n" \
               " |\n" \
               " |\n" \
               "_|_ _ _"

    HANGMAN5 = " _____\n" \
               " |/  |\n" \
               " |   0\n" \
               " |\n" \
               " |\n" \
               "_|_ _ _"

    HANGMAN6 = " _____\n" \
               " |/  |\n" \
               " |   o\n" \
               " |   |\n" \
               " |\n" \
               "_|_ _ _"

    HANGMAN7 = " _____\n" \
               " |/  |\n" \
               " |   o\n" \
               " |  /|\n" \
               " |\n" \
               "_|_ _ _"

    HANGMAN8 = " _____\n" \
               " |/  |\n" \
               " |   o\n" \
               " |  /|\ \n" \
               " |\n" \
               "_|_ _ _"

    HANGMAN9 = " _____\n" \
               " |/  |\n" \
               " |   o\n" \
               " |  /|\ \n" \
               " |  /\n" \
               "_|_ _ _"

    HANGMAN10 = " _____\n" \
                " |/  |\n" \
                " |   o\n" \
                " |  /|\ \n" \
                " |  / \ \n" \
                "_|_ _ _"

    hangmen = [HANGMAN0, HANGMAN1, HANGMAN2, HANGMAN3, HANGMAN4, HANGMAN5, HANGMAN6, HANGMAN7, HANGMAN8, HANGMAN9, HANGMAN10]

    HMRULES = "Try to guess the hidden word.\n" \
              "There are only lowercase letters in the word.\n" \
              "Press the indicated reactions on the message to make your move.\n" \
              "Press " + STOP_EMOJI + " to close the game.\n"

def on_startup():
    global randwords

    with open("data/10k_words.txt") as f:
        randwords = f.readlines()
    f.close()

def getRandomWord():
    global randwords
    num_lines = sum(1 for line in open('data/10k_words.txt'))
    return randwords[random.randint(0, num_lines)].rstrip()

def get_next_midnight_stamp():
    datenow = datetime.date.today() + datetime.timedelta(days=1)
    unix_next = datetime.datetime(datenow.year, datenow.month, datenow.day, 0)
    unixtime = time.mktime(unix_next.timetuple())
    return unixtime

def increment_game(game):
    Variables.amtPlayedGames[game] = int(Variables.amtPlayedGames[game]) + 1
