import os
from enum import Enum

from discord import Color

from yaml import safe_load

DEV_MODE = True

log_channel = 728570503169704014
contact_channel = 728570526443896934
support_channel = 728570540998262834
bug_report_channel = 728570578507923526
suggestions_channel = 728570594899132456
complaints_channel = 728570619985264650

creator = "The-Codin-Hole team"
devs = [688275913535914014, 306876636526280705, 710400991761137666]

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

SUPPORT_SERVER = "https://discord.gg/7e9zKFr"


COMMAND_PREFIX = os.environ.get("COMMAND_PREFIX", ">>")

paste_link = "https://pastebin.com"
paste_link_2 = "https://hastebin.com"

line_img_url = "https://cdn.discordapp.com/attachments/581139962611892229/692712698487767080/animated_line.gif"

# Magic 8-Ball responses
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

# NSFW Command Possible types
nsfw_possible = [
    "feet", "yuri", "trap", "futanari", "hololewd", "lewdkemo",
    "solog", "feetg", "cum", "erokemo", "les", "wallpaper",
    "lewdk", "ngif", "tickle", "lewd", "feed", "gecg",
    "eroyuri", "eron", "cum_jpg", "bj", "nsfw_neko_gif", "solo",
    "kemonomimi", "nsfw_avatar", "gasm", "poke", "anal", "slap",
    "hentai", "avatar", "erofeet", "holo", "keta", "blowjob",
    "pussy", "tits", "holoero", "lizard", "pussy_jpg", "pwankg",
    "classic", "kuni", "waifu", "pat", "8ball", "kiss",
    "femdom", "neko", "spank", "cuddle", "erok", "fox_girl",
    "boobs", "random_hentai_gif", "smallboobs", "hug", "ero", "smug",
    "goose", "baka", "woof",
]

# Possible HTTP Codes for HttpCat
http_codes = [
    100, 101, 200, 201, 202, 204, 206, 207, 300, 301,
    302, 303, 304, 305, 307, 400, 401, 402, 403, 404,
    405, 406, 408, 409, 410, 411, 412, 413, 414, 416,
    417, 418, 420, 421, 422, 423, 424, 425, 426, 429,
    444, 450, 451, 500, 502, 503, 504, 506, 507, 508,
    509, 511, 599,
]

# Search Engine categories
basic_search_categories = [
    "web",
    "videos",
    "music",
    "files",
    "images",
    "it",
    "maps",
]

nekos = {
    "sfw": "https://nekos.life/api/neko",
}


with open("bot/assets/languages.yml", "r") as file:
    default_languages = safe_load(file)


# Emojis class
class Emojis:
    issue = "<:IssueOpen:725770366714380410>"
    issue_closed = "<:IssueClosed:725770497039663114>"
    pull_request = "<:PROpen:725770558582554744>"
    pull_request_closed = "<:PRClosed:725770652354609234>"
    merge = "<:PRMerged:725770703600615435>"


class Infraction(Enum):
    warning = Color.gold()
    kick = Color.gold()
    ban = Color.red()


class SuggestionStatus(Enum):
    under_review = "Under review"
    denied = "Denied"
    approved = "Approved"
