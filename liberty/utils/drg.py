import discord
import json
import requests

DOMAIN_URL = 'https://doublexp.net/'
class DRGUtils():
    @staticmethod
    def fetch_missions_metadata(season=0):
        mission_data = requests.get(f'{DOMAIN_URL}json?data=current').content
        mission_data = json.loads(mission_data)

        biomes = {}
        for biome, missions in mission_data['Biomes'].items():
            biomes[biome] = []
            for mission in missions:
                if f's{season}' in mission['included_in']:
                    mission['icon_url'] = f'{DOMAIN_URL}/png?img={mission["CodeName"].replace(" ", "-")}{str(mission["id"])}'
                    biomes[biome].append(mission)

        return biomes

    @staticmethod
    def create_mission_embed(biome, mission_icon):
        # This is a little cursed. Apparently discord will aggregate embeds sent in
        # the same message as long as they have the same url set. This allows us to
        # display 4 mission icons in one embed, greatly cleaning up the channel
        # 2 main issues: one, it looks like garbage. Two, it only actually displays 4
        # images max, even if there are more. You have to click in and scroll through
        # to see the rest.
        # Future solution: keep a count of how many we've made. The first embed gets a
        # title (use the biome I guess), and then after 4 we choose a new url to aggregate
        # separately? Very cursed.
        embed = discord.Embed(url='https://doublexp.net', color=discord.Color.blue())
        embed.set_image(url=mission_icon)
        return embed

    @staticmethod
    def array_mission_embeds(biomes=None):
        if not biomes:
            biomes = DRGUtils.fetch_missions_metadata()
        biomes_embeds = {}

        for biome, missions in biomes.items():
            biomes_embeds[biome] = []
            for mission in missions:
                mission_embed = DRGUtils.create_mission_embed(biome, mission['icon_url'])
                biomes_embeds[biome].append(mission_embed)

        return biomes_embeds
