from enum import Enum

from discord import Color

youtube_url = "https://www.youtube.com/channel/UC3S4lcSvaSIiT3uSRSi7uCQ"
ig_url = "https://instagram.com/the.codin.hole/"

github_repo_link = "https://github.com/janaSunrise/HotWired-Bot"
discord_server = "https://discord.gg/CgH6Sj6"

invite_link = "https://discord.com/api/oauth2/authorize?client_id=715545167649570977&permissions=2020835191" \
			  "&redirect_uri=https%3A%2F%2Fdiscord.gg%2FvP26dCy&scope=bot "

admin_invite_link = "https://discord.com/api/oauth2/authorize?client_id=715545167649570977&permissions=8" \
					"&redirect_uri=https%3A%2F%2Fdiscord.gg%2FvP26dCy&scope=bot "

line_img_url = "https://cdn.discordapp.com/attachments/581139962611892229/692712698487767080/animated_line.gif"

class Infraction(Enum):
	warning = Color.gold()
	kick = Color.gold()
	ban = Color.red()


class SuggestionStatus(Enum):
	under_review = "Under review"
	denied = "Denied"
	approved = "Approved"
