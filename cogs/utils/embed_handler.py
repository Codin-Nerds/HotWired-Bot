from discord import Color, Embed, Member, Status

from cogs.utils.members import get_member_activity, get_member_roles_as_mentions, get_member_status


def status_embed(member: Member, *, description: str = "") -> Embed:
    """Construct status embed for certain member."""
    embed = Embed(title=member.display_name, description=description, color=Color.dark_purple())

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
