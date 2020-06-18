from enum import Enum

from discord import Color

DEV_MODE = True

owner_id = 688275913535914014
log_channel = 704197974577643550
creator = "The-Codin-Hole team"
devs = [710400991761137666, 688275913535914014, 306876636526280705]

youtube_url = "https://www.youtube.com/channel/UC3S4lcSvaSIiT3uSRSi7uCQ"
ig_url = "https://instagram.com/the.codin.hole/"

github_repo_link = "https://github.com/The-Codin-Hole/HotWired-Bot"
discord_server = "https://discord.gg/CgH6Sj6"

invite_link = (
    "https://discord.com/api/oauth2/authorize?client_id=715545167649570977&permissions=2020835191"
    "&redirect_uri=https%3A%2F%2Fdiscord.gg%2FvP26dCy&scope=bot "
)

admin_invite_link = (
    "https://discord.com/api/oauth2/authorize?client_id=715545167649570977&permissions=8"
    "&redirect_uri=https%3A%2F%2Fdiscord.gg%2FvP26dCy&scope=bot "
)

SUPPORT_SERVER = "https://discord.gg/CgH6Sj6"

COMMAND_PREFIX = ">>"

line_img_url = "https://cdn.discordapp.com/attachments/581139962611892229/692712698487767080/animated_line.gif"

NEGATIVE_REPLIES = [
    "Noooooo!!",
    "Nope.",
    "I'm sorry Dave, I'm afraid I can't do that.",
    "I don't think so.",
    "Not gonna happen.",
    "Out of the question.",
    "Huh? No.",
    "Nah.",
    "Naw.",
    "Not likely.",
    "No way, José.",
    "Not in a million years.",
    "Fat chance.",
    "Certainly not.",
    "NEGATORY.",
    "Nuh-uh.",
    "Not in my house!",
]

POSITIVE_REPLIES = [
    "Yep.",
    "Absolutely!",
    "Can do!",
    "Affirmative!",
    "Yeah okay.",
    "Sure.",
    "Sure thing!",
    "You're the boss!",
    "Okay.",
    "No problem.",
    "I got you.",
    "Alright.",
    "You got it!",
    "ROGER THAT",
    "Of course!",
    "Aye aye, cap'n!",
    "I'll allow it.",
]

ERROR_REPLIES = [
    "Please don't do that.",
    "You have to stop.",
    "Do you mind?",
    "In the future, don't do that.",
    "That was a mistake.",
    "You blew it.",
    "You're bad at computers.",
    "Are you trying to kill me?",
    "Noooooo!!",
    "I can't believe you've done this",
]


class Infraction(Enum):
    warning = Color.gold()
    kick = Color.gold()
    ban = Color.red()


class SuggestionStatus(Enum):
    under_review = "Under review"
    denied = "Denied"
    approved = "Approved"
