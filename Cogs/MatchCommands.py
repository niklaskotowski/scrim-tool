import discord
from discord.ext import commands
import scrimdb as db
import logging
from datetime import datetime

# brainstorm 
# match structure
# datetime object
# team #1
# roster 1
# team #2
# roster 2


class MatchCommands(commands.Cog, name="MatchCommands"):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Match commands loaded")


    @commands.command(name="match_create",
                      usage="<TeamName>")
    async def match_create(self, ctx, team_name, date, time):
        # match_create team_name, day/month hour:minutes
        date_split = date.split("/")
        time_split = time.split(":")
        dt = datetime(2022, int(date_split[1]), int(date_split[0]), int(time_split[0]), int(time_split[1]))

        result = db.create_match(ctx.author, team_name, dt)
        status = result['status']

        send_msg = ""
        if status == "team_notfound":
            send_msg = f"The named team has not been found.\n"
        elif status == "not_owner":
            send_msg = f"Only the team owner is allowed to schedule a match.\n"
        elif status == "created":
            send_msg = f"A match has been scheduled to {dt}.\n"
        await ctx.author.send(send_msg)        

    @commands.command(name="match_show_all")
    async def match_show_all(self, ctx):
        result = db.get_all_matches(ctx.author)
        status = result['status']

        send_msg = ""
        if status == "success":
            embed=discord.Embed()
            embed.set_author(name="Currently open matches:")
            embed.add_field(name="Time:", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Team 1:", value="OlsCs", inline=True)
            embed.add_field(name="Roster:", value="Secr3t\nVictoriousMuffin\nCpt Aw\n", inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=False)
            embed.add_field(name="Team 2:", value="OlsCock", inline=True)
            embed.add_field(name="Roster:", value="Diviine\nRalle\nGabi ", inline=True)
        await ctx.send(embed=embed)       

    # show all scrim dates for a given team 
    @commands.command(name="match_show",
                      usage="<TeamName>")
    async def match_show(self, ctx, team_name):
        result = db.get_match(ctx.author, team_name)
        status = result['status']

        send_msg = ""
        if status == "success":
            for match in result['matches']:
                embed=discord.Embed()
                string = "Currently scheduled scrim matches for '" + team_name + "'"
                embed.set_author(name=string)
                embed.add_field(name="Time:", value=match['datetime'], inline=False)
                embed.add_field(name="Team 1:", value=match['team1'], inline=True)
                # concat members in a string
                members1 = [x for x in match['roster1']]
                mem1_str = "\n".join(members1)
                if mem1_str == "":
                    mem1_str = "Currently no player in this team."
                embed.add_field(name="Roster:", value=mem1_str, inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=False)
                embed.add_field(name="Team 2:", value=match['team2'], inline=True)
                members2 = [x for x in match['roster2']]
                mem2_str = "\n".join(members2)
                if mem2_str == "":
                    mem2_str = "Currently no player in this team."
                embed.add_field(name="Roster:", value=mem2_str, inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=False)
                embed.add_field(name="Matchcode:", value= match['_id'], inline=False)
                message = await ctx.send(embed=embed) 
                #one emoji to define joining a team and one emoji to specify joining the scrim as a player
                emoji = '\N{THUMBS UP SIGN}'
                message.add_reaction(emoji)
        elif status == "team_notfound":
            send_msg = f"Team not found.\n"
            await ctx.author.send(send_msg) 
           
    # join a match as a team -- organized by emotes that can be upvoted
    @commands.command(name="match_team_join",
                      usage="<TeamName>")
    async def match_team_join(self, ctx, _id):
        result = db.join_match_asteam(ctx.author, _id)
        status = result['status']

        send_msg = ""
        if status == "success":
            send_msg = f" {result['team_name']} joined the scrim.\n"
        elif status == "already_part_of_it":
            send_msg = f"The team  {result['team_name']} is already part of the scrim.\n"
        elif status == "team_notfound":
            send_msg = f"You have to own a team in order to join a scrim.\n"
        await ctx.author.send(send_msg)  

    # join a match as a player -- organized by emotes that can be upvoted
    @commands.command(name="match_player_join",
                      usage="<TeamName>")
    async def match_player_join(self, ctx, _id):
        result = db.join_match_asplayer(ctx.author, _id)
        status = result['status']

        send_msg = ""
        if status == "success":
            send_msg = f"You joined the scrim on {result['scrim']['datetime']}.\n"
            match_show(ctx, result['scrim']['team1'])
        elif status == "no_member":
            send_msg = f"You have to be part of one of the teams in order to join the scrim as a player'.\n"
        elif status == "already_part_of_it":
            send_msg = f"You are already part of the scrim.\n"
        await ctx.author.send(send_msg)        

    async def update_roster(self, ctx, match, team_nr, roster):
        print("update roster")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        channel = self.bot.get_channel(956618562712264765)
        if str(reaction.emoji) == "🙌":        
            message = await channel.fetch_message(reaction.message_id)
            embeds = message.embeds
            e = embeds[0].to_dict()
            match_id = e['fields'][-1]['value']
            #messsage.edit(embed = newEmbed)
            result = db.join_match_asplayer(reaction.user_id, match_id)
            status = result['status']
            send_msg = ""
            if status == "success":
                match = result['match']
                embed=discord.Embed()
                string = "Scrim"
                embed.set_author(name=string)
                embed.add_field(name="Time:", value=match['datetime'], inline=False)
                embed.add_field(name="Team 1:", value=match['team1'], inline=True)
                # concat members in a string
                members1 = [str(x) for x in result['players']]
                mem1_str = "\n".join(members1)
                if mem1_str == "":
                    mem1_str = "Currently no player in this team."
                embed.add_field(name="Roster:", value=mem1_str, inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=False)
                embed.add_field(name="Team 2:", value=match['team2'], inline=True)
                members2 = [str(x) for x in result['players']]
                mem2_str = "\n".join(members2)
                if mem2_str == "":
                    mem2_str = "Currently no player in this team."
                embed.add_field(name="Roster:", value=mem2_str, inline=True)
                embed.add_field(name='\u200b', value='\u200b', inline=False)
                embed.add_field(name="Matchcode:", value= match['_id'], inline=False)     
                await message.edit(embed = embed)
            elif status == "no_member":
                send_msg = f"You have to be part of one of the teams in order to join the scrim as a player'.\n"
                await channel.send(send_msg)
            elif status == "already_part_of_it":
                send_msg = f"You are already part of the scrim.\n"
                await channel.send(send_msg)
            elif status == "match_notfound":
                send_msg = f"Match not found"
                await channel.send(send_msg)       

####Error Handling


            
def setup(bot):
    bot.add_cog(MatchCommands(bot))