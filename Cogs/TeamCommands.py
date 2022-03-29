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
        print("team_create")
        result = db.create_team(ctx.author, arg)
        status = result['status']
        print(status)
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
            send_msg = f"No team named '{arg1}' has been found in the databse.\n"
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
            send_msg = f"No team named '{arg1}' has been found in the databse.\n"
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
        print("under construction")

    @commands.command(name="team_list")
    async def team_list(self, ctx, arg1):
        #list team all existing teams and their member count 
        print("under construction")

    @team_create.error
    async def team_create_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a Team Name\nUsage: !link <TeamName>")
            
def setup(bot):
    bot.add_cog(TeamCommands(bot))
    print("Log: TeamCommands is loaded.")