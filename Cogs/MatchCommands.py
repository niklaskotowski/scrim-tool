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
swords = "\u2694\uFE0F"
raised_hand = "\u270B"
exit = 	"\u274C"
check = "\u2705"

def construct_Embeds(title, match, players_t1, players_t2, team_idx = 0):
    embed=discord.Embed()        
    embed.set_author(name=title)
    embed.add_field(name="Time:", value=match['datetime'], inline=False)
    if (match['team1'] == ""):
        match['team1'] = '\u200b'
    embed.add_field(name="Team 1:", value=match['team1'], inline=True)
    # concat members in a string
    members1 = [str(x) for x in players_t1[team_idx]]
    mem1_str = "\n".join(members1)
    if mem1_str == "":
        mem1_str = "Currently no player in this team."
    embed.add_field(name="Roster:", value=mem1_str, inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=False)
    if (match['team2'] == ""):
        match['team2'] = '\u200b'
    embed.add_field(name="Team 2:", value=match['team2'], inline=True)
    members2 = [str(x) for x in players_t2[team_idx]]
    mem2_str = "\n".join(members2)
    if mem2_str == "":
        mem2_str = "Currently no player in this team."
    embed.add_field(name="Roster:", value=mem2_str, inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=False)
    embed.add_field(name="Matchcode:", value= match['_id'], inline=False)
    return embed

class MatchCommands(commands.Cog, name="MatchCommands"):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

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
            idx = 0
            for match in result['matches']:
                title = "Currently open scrim matches: "
                embed = construct_Embeds(title, match, result['players_t1'], result['players_t2'], idx)
                idx = idx + 1
                message = await ctx.send(embed = embed)       
                await message.add_reaction(check)
                await message.add_reaction(exit)

    # show all scrim dates for a given team 
    @commands.command(name="match_show",
                      usage="<TeamName>")
    async def match_show(self, ctx, team_name):
        result = db.get_match(ctx.author, team_name)
        status = result['status']
        if status == "success":
            i = 0
            title = "Currently scheduled scrim matches for '" + team_name + "'"
            for match in result['matches']:
                embed = construct_Embeds(title, match, result['players_t1'], result['players_t2'], i)
                message = await ctx.send(embed=embed) 
                #one emoji to define joining a team and one emoji to specify joining the scrim as a player
                await message.add_reaction(check)
                await message.add_reaction(exit)
                i = i+1
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
            send_msg = f"You joined the scrim on {result['match']['datetime']}.\n"
            title = "Match:"
            embed = construct_Embeds(title, result['match'], result['players_t1'], result['players_t2'])
            message = await ctx.send(embed=embed) 
            #one emoji to define joining a team and one emoji to specify joining the scrim as a player
            await message.add_reaction(check)
            await message.add_reaction(exit)
        elif status == "no_member":
            send_msg = f"You have to be part of one of the teams in order to join the scrim as a player'.\n"
        elif status == "already_part_of_it":
            send_msg = f"You are already part of the scrim.\n"
        await ctx.author.send(send_msg)        

    async def update_roster(self, ctx, match, team_nr, roster):
        print("update roster")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        #cases we have to divide
        #(1) you want to join as a player
        #(2) you want to join as a team
        #(3) you want to leave as a player
        #(4) you want to leave with your team
        #each player can only be part of one team, thus we merge (1) & (2) and (3) & (4)
        if (reaction.member.bot == True):
            return
        channel = self.bot.get_channel(956618562712264765)
        message = await channel.fetch_message(reaction.message_id)
        embeds = message.embeds
        e = embeds[0].to_dict()
        match_id = e['fields'][-1]['value']
        if str(reaction.emoji) == raised_hand:    
            #obtain the embed in which message infos are saved
            #match_id currently saved in the bottom row of the embed            
            result = db.join_match_asplayer(reaction.user_id, match_id)
            status = result['status']
            send_msg = ""
            if status == "success":
                title = "Scrim"
                embed = construct_Embeds(title, result['match'], result['players_t1'], result['players_t2']) 
                await message.edit(embed=embed)
            elif status == "no_member":
                send_msg = f"You have to be part of one of the teams in order to join the scrim as a player'.\n"
                await channel.send(send_msg)
            elif status == "already_part_of_it":
                send_msg = f"You are already part of the scrim.\n"
                await channel.send(send_msg)
            elif status == "match_notfound":
                send_msg = f"Match not found"
                await channel.send(send_msg)   
        #team wants to enter scrim 
        if str(reaction.emoji) == swords:          
            result = db.join_match_asteam(reaction.user_id, match_id)
            status = result['status']
            if status == "success":
                title = "Scrim"
                embed = construct_Embeds(title, result['match'], result['players_t1'], result['players_t2']) 
                await message.edit(embed=embed)
            elif status == "not_owner":
                await channel.send(f"You have to own a team in order to join a scrim'.\n")
            elif status == "already_part_of_it":         
                await channel.send(f"The team is already part of the scrim.\n")
            elif status == "full":
                await channel.send(f"The scrim is already full.\n")
        if str(reaction.emoji) == check:
            # possible intentions
            # want to join as a player, want to join as a team
            # cases:
            # -> player does not own a team and his team is not participating
            # -> player does own a team-> requests to join with his team
            # -> player is member of a team -> requests to join as a plaer
            teamOwner = db.getTeamByOwnerID(reaction.user_id)
            teamMember = db.getTeamByMemberID(reaction.user_id)
            if (teamOwner['status'] == "success"):
                result = db.join_match_asTeam(reaction.user_id, match_id)
                if (result['status'] == "fail"):
                    assert(False)
                elif (result['status'] == "success"):
                    title = "Scrim"
                    embed = construct_Embeds(title, result['match'], result['players_t1'], result['players_t2']) 
                    await message.edit(embed=embed)
            if (teamMember['status'] == "success"):
                result = db.join_match_asPlayer(reaction.user_id, match_id)
                title = "Scrim"
                embed = construct_Embeds(title, result['match'], result['players_t1'], result['players_t2']) 
                await message.edit(embed = embed)
        if str(reaction.emoji) == exit:
            # it should be possible that the owner leaves the scrim without removing the team from the scrim
            # initially we have to verify that the player is part of the scrim, thus we start with leave match as player:
            # in case we receive a negative response we continue by attempting to remove the team
            # cases:
            # -> player is not part of the scrim nor is his team => return ;
            # -> player is not part of the scrim but his team => remove team
            # -> player is part of the scrim => remove player
            team = db.getTeamByOwnerID(reaction.user_id)
            if (db.isPlayerInScrim(reaction.user_id, match_id)):
                result = db.leave_match_asPlayer(reaction.user_id, match_id)
                if (result['status'] == "fail"):
                    assert(False)
                else: 
                    title = "Scrim"
                    embed = construct_Embeds(title, result['match'], result['players_t1'], result['players_t2']) 
                    await message.edit(embed=embed)                    
            elif(team['status'] == "success"):
                if(db.isTeamInScrim(team['team']['name'], match_id)):
                    result = db.leave_match_asTeam(reaction.user_id, match_id)
                    if (result['status'] != "fail"):
                        title = "Scrim"
                        embed = construct_Embeds(title, result['match'], result['players_t1'], result['players_t2']) 
                        await message.edit(embed=embed)
            
def setup(bot):
    bot.add_cog(MatchCommands(bot))