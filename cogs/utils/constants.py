from enum import Enum

from discord import Color

youtube_url = "https://www.youtube.com/channel/UC3S4lcSvaSIiT3uSRSi7uCQ"
ig_url = "https://instagram.com/the.codin.hole/"
github_repo_link = "https://github.com/janaSunrise"
line_img_url = "https://cdn.discordapp.com/attachments/581139962611892229/692712698487767080/animated_line.gif"

class Infraction(Enum):
    warning = Color.gold()
    kick = Color.gold()
    ban = Color.red()


class SuggestionStatus(Enum):
    under_review = "Under review"
    denied = "Denied"
    approved = "Approved"
