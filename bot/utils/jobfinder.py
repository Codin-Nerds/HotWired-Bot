import requests
import random as rd
import html
import datetime

from discord import Embed

from bs4 import BeautifulSoup


class Job:
    def __init__(self, *args, **attrs):
        self.title = attrs['title']
        self.id = attrs['id']
        self.updated_at = attrs['updated_at']

        self.departments = attrs['departments']
        self.location = attrs['location']

        self.link = attrs['link']
        self.data_compliance = attrs.get('data_compliance', None)

        self._content = html.unescape(attrs['content'])

    def embed(self):
        soup = BeautifulSoup(self._content, 'html.parser')
        colors = [
            0x4e8dd0,
            0xc33cbf,
            0x42cd59
        ]
        embed = Embed(
            title=self.title,
            description="**Description:** " + soup.find('h2').text + "...",
            url=self.link,
            color=colors[rd.randint(0, 2)]
        )

        embed.add_field(name="Department", value=", ".join([department['name'] for department in self.departments]))

        embed.add_field(name='Last Updated', value=f"Job id {self.id} updated last at {self.updated_at}.")

        return embed


class DiscordJobFinder:
    def __init__(self):
        self._jobs = []

        jobscontent = "https://api.greenhouse.io/v1/boards/discord/jobs?content=true"
                
        jobs = requests.get(jobscontent, headers={"User-Agent": "Job Scraper (Discord Bot)"}).json()['jobs']
                

        for job in jobs:
            job = {
                'title': job['title'],
                'id': job['id'],
                'updated_at': datetime.datetime.fromisoformat(job['updated_at']),
                'departments': job['departments'],
                'location': job['location']['name'],
                'link': 'https://discord.com/new/jobs/{}'.format(job['id']),
                'data_compiance': job['data_compliance'],
                'content': job['content']
            }

            self.jobs.append(Job(**job))

    @property
    def jobs(self):
        return self._jobs


finder = DiscordJobFinder()
