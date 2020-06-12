import discord
from discord.ext import commands
from utils.geolocation import get_loc_data


class Hacking(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def iplookup(self, ctx, ipaddr):
        data = get_loc_data(ipaddr)

        if isinstance(data, dict):
            try:
                city = data['city']
                region = data['region']
                country = data['country']
                country_capital = data['country_capital']
                country_tld = data['country_tld']
                postal = data['postal']
                utc_offset = data['utc_offset']
                currency = data['currency']
                languages = data['languages'].split(',')
                asn = data['asn']
                org = data['org']

                loc_data = f"""
                            • City : {city}
                            • Region : {region}
                            • Country : {country}
                            • Country Capital : {country_capital}
                        """
                basic_data = f"""
                            • Postal : {postal}
                            • UTC Offset : {utc_offset}
                            • Currency : {currency}
                            • Languages : {languages}
                        """
                online_data = f"""
                            • Country TLD : {country_tld}
                            • ASN : {asn}
                            • Organization : {org}
                        """

                embed = discord.Embed(
                    title="IP Address Geolocation Data",
                    color=discord.Color.dark_green()
                )
                embed.add_field(name="**❯❯ Locational Data**", value=loc_data, inline=False)
                embed.add_field(name="**❯❯ Basic Data**", value=basic_data, inline=False)
                embed.add_field(name="**❯❯ Online Data**", value=online_data, inline=False)

                await ctx.send(embed=embed)


            except:
                error = data['error']
                reason = data['reason']

                embed = discord.Embed(
                    title="ERROR!",
                    description=reason,
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=data,
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Hacking(client))
