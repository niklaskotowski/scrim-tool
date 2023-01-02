
import scrimdb as db
import interactions

class UserCommands(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    
    @interactions.extension_command(
        name="unlink",
        description="Unlink your Riot Account!",
        scope=271639846307627008,
    )
    async def unlink(self, ctx):
        dels = db.unlink_command(ctx.author)
        await ctx.send(f"Removed Links: {dels}")

    @interactions.extension_command(
        name="link",
        description="Link your Riot Account!",
        scope=271639846307627008,
    )
    async def link(self, ctx):
        SummonerNameInput = interactions.TextInput(
            style=interactions.TextStyleType.SHORT,
            label="Enter your summoner name:",
            custom_id="text_input_response",
            min_length=1,
            max_length=20,
        )
        modalSummonerNameInput = interactions.Modal(
            title="Summoner Name",
            custom_id="link_account",
            components=[SummonerNameInput],
        )
        await ctx.popup(modalSummonerNameInput)

    @interactions.extension_modal("link_account") 
    async def link_user(self, ctx, response: str):
        db.link_command(response, ctx.author)
        await ctx.send("Successful account linkage", ephemeral=False)

    
    @interactions.extension_command(
        name="ranked_info",
        description="Show ranked info of linked Riot Account!",
        scope=271639846307627008,
    )
    async def rankedinfo(self, ctx):
        db_response = db.rankedinfo_command(ctx.author)
        await ctx.send(db_response.discord_msg())





def setup(client):
    UserCommands(client)