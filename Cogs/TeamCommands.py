import discord
from discord.ext import commands
import scrimdb as db
import logging

class TeamCommands(commands.Cog, name="TeamCommands"):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Team Commands loaded")


    @commands.command(name="team_create",
                      usage="<TeamName>")
    async def team_create(self, ctx, arg):
        result = db.create_team(ctx.author, arg)
        status = result['status']

        send_msg = ""
        if status == "created":
            send_msg = f"Your League team '{arg}' has been created.\n"
        elif status == "not_verified":
            send_msg = f"You have to link your league account before creating a team '!link <SummonerName>'.\n"
        elif status == "exists":
            send_msg = f"A team with this name does already exist.\n"
        await ctx.author.send(send_msg)                
        

    @commands.command(name="team_invite",
                      usage="<TeamName> <PlayerName>")
    async def team_invite(self, ctx, arg1, user: discord.Member = None):
        invitation = db.invite_user(ctx.author, arg1, user)
        status = invitation['status']

        send_msg = ""
        if status == "team_notfound":
            send_msg = f"No team named '{arg1}' has been found in the database.\n"
        elif status == "invitee_not_verified":
            send_msg = f"The player you are trying to invite is not verified.\n"
        elif status == "not_owner":
            send_msg = f"Only the team owner is allowed to invite new players.\n"
        elif status == "success":
            send_msg = f"{user.name} has been successfully invited to '{arg1}'.\n"
        await ctx.author.send(send_msg)

    @commands.command(name="team_join",
                      usage="<TeamName>")
    async def team_join(self, ctx, arg1):
        result = db.join_team(ctx.author, arg1)
        status = result['status']

        send_msg = ""
        if status == "team_notfound":
            send_msg = f"No team named '{arg1}' has been found in the database.\n"
        elif status == "no_invitation":
            send_msg = f"No open invitation for {ctx.author}.\n"
        elif status == "not_verfied":
            send_msg = f"You have to be verified before interacting with teams.\n"
        elif status == "success":
            send_msg = f"You successfully joined '{arg1}'.\n"
        else:
            assert(false)
        await ctx.author.send(send_msg)

    @commands.command(name="team_leave")
    async def team_leave(self, ctx, arg1):
        result = db.leave_team(ctx.author, arg1)
        status = result['status']

        send_msg = ""
        if status == "team_notfound":
            send_msg = f"No team named '{arg1}' has been found in the database.\n"
        elif status == "no_member":
            send_msg = f"You are not a member of '{arg1}'."
        elif status == "success":
            send_msg = f"You successfully left '{arg1}'."
        else:
            assert(false)
        await ctx.author.send(send_msg)

    @commands.command(name="team_delete")
    async def team_delete(self, ctx, arg1):
        result = db.remove_team(ctx.author, arg1)
        status = result['status']

        send_msg = ""
        if status == "team_notfound":
            send_msg = f"No team named '{arg1}' has been found in the database.\n"
        elif status == "not_owner":
            send_msg = f"You are not the owner of '{arg1}'."
        elif status == "success":
            send_msg = f"You successfully deleted '{arg1}'."
        else:
            assert(false)

        await ctx.author.send(send_msg)

    @commands.command(name="team_show")
    async def team_show(self, ctx, arg1):
        #list team members
        #list avg elo
        #list w/l ratio
        result = db.get_team(ctx.author, arg1)
        print(result)
        print(ctx)
        status = result['status']
        if status == "team_notfound":
            send_msg = f"No team named '{arg1}' has been found in the database.\n"
            await ctx.author.send(send_msg)
        else:
            send_msg = f"Teamname: {arg1}\n "
            for x in result['members']:
                send_msg += f"Player: {x.summoner_name}"
            await ctx.send(send_msg) 

    @commands.command(name="team_list")
    async def team_list(self, ctx):
        #list team all existing teams and their member count 
        result = db.get_all_teams(ctx.author)
        status = result['status']
        send_msg = "\n"
        for team in result['teams']:
            send_msg += f"Teamname: {team['name']}.\n"

        await ctx.send(send_msg)

####Error Handling
    @team_create.error
    async def team_create_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_create <TeamName>")

    @team_invite.error
    async def team_invite_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name and specify a player\nUsage: !team_invite <TeamName> <PlayerName>")

    @team_join.error
    async def team_join_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_join <TeamName>")

    @team_leave.error
    async def team_leave_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_leave <TeamName>")

    @team_delete.error
    async def team_delete_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_delete <TeamName>")

    @team_show.error
    async def team_leave_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_show <TeamName>")


            
def setup(bot):
    bot.add_cog(TeamCommands(bot))