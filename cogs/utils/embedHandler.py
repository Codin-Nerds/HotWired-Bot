from typing import Union

from discord import Embed, Color, Member, User, Status

from cogs.utils import constants
from cogs.utils.members import get_member_status, get_member_roles_as_mentions, get_member_activity


def simple_embed(message: str, title: str, color: Color) -> Embed:
    embed = Embed(title=title, description=message, color=color)
    return embed


def welcome_dm(message: str) -> Embed:

    content_footer = (f"Links: [Youtube Channel]({constants.youtube_url}) | "
                      f"[Instagram]({constants.ig_url})")
    message = f"{message}\n\n{content_footer}"
    welcome_dm_embed = simple_embed(message, "Welcome", color=Color.dark_green())
    welcome_dm_embed.set_image(url=constants.line_img_url)
    return welcome_dm_embed


def welcome(message: str) -> Embed:

    return simple_embed(message, "Welcome!", color=Color.dark_green())


def goodbye(message: str) -> Embed:

    return simple_embed(message, "Goodbye", color=Color.dark_red())


def info(message: str, member: Union[Member, User], title: str = "Info") -> Embed:

    return Embed(title=title, description=message, color=get_top_role_color(member, fallback_color=Color.green()))


def success(message: str, member: Union[Member, User] = None) -> Embed:

    return simple_embed(message, "Success", get_top_role_color(member, fallback_color=Color.green()))


def warning(message: str) -> Embed:

    return simple_embed(message, "Warning", Color.dark_gold())


def failure(message: str) -> Embed:

    return simple_embed(message, "Failure", Color.red())

def error_embed(message: str, title: str = "Error") -> Embed:

    return simple_embed(message, title, Color.red())


def authored(message: str, *, author: Union[Member, User]) -> Embed:

    embed = Embed(description=message, color=get_top_role_color(author, fallback_color=Color.green()))
    embed.set_author(name=author.name, icon_url=author.avatar_url)
    return embed


def thumbnail(message: str, member: Union[Member, User], title: str = None) -> Embed:
    
    embed = Embed(title=title, description=message, color=get_top_role_color(member, fallback_color=Color.green()))
    embed.set_thumbnail(url=str(member.avatar_url))
    return embed


def status_embed(member: Member, *, description: str = "") -> Embed:

    embed = Embed(
        title=member.display_name,
        description=description,
        color=get_top_role_color(member, fallback_color=Color.green())
    )

    if member.status == Status.offline:
        embed.add_field(name="**DEVICE**", value=":no_entry:")
    elif member.is_on_mobile():
        embed.add_field(name="**DEVICE**", value="Phone: :iphone:")
    else:
        embed.add_field(name="**DEVICE**", value="PC: :desktop:")

    embed.add_field(name="**Status**", value=get_member_status(member=member), inline=False)
    embed.add_field(name="**Joined server at**", value=member.joined_at, inline=False)
    embed.add_field(name="**Roles**", value=get_member_roles_as_mentions(member), inline=False)
    embed.add_field(name="**Activity**", value=get_member_activity(member=member), inline=False)
    embed.set_thumbnail(url=member.avatar_url)

    return embed


def infraction_embed(
        ctx,
        infracted_member: Union[Member, User],
        infraction_type: constants.Infraction,
        reason: str
) -> Embed:

    embed = Embed(title="**Infraction information**", color=infraction_type.value)
    embed.set_author(name="The Codin' Hole", icon_url=ctx.me.avatar_url)

    embed.add_field(name="**Member**", value=f"{infracted_member}", inline=False)
    embed.add_field(name="**Type**", value=infraction_type.name, inline=False)
    embed.add_field(name="**Reason**", value=reason, inline=False)
    return embed


def get_top_role_color(member: Union[Member, User], *, fallback_color) -> Color:

    try:
        color = member.top_role.color
    except AttributeError:
        # Fix for DMs
        return fallback_color

    if color == Color.default():
        return fallback_color
    else:
        return color