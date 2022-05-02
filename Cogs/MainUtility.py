import discord
from discord.ext import commands
import scrimdb as db
import interactions

class MainUtility(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Log:", self.bot.user)

    # @interactions.extension_command(
    #     name="hw",
    #     description="This is the first command I made!",
    #     scope=271639846307627008,
    # )
    # async def hw(self, ctx):
    #     await ctx.send("BASTARD")
    
    # @interactions.extension_command(
    #     name="textinput",
    #     description="This is a textinput command",
    #     scope=271639846307627008,
    # )
    # async def my_cool_modal_command(self, ctx):
    #     tI = interactions.TextInput(
    #         style=interactions.TextStyleType.SHORT,
    #         label="Let's get straight to it: what's 1 + 1?",
    #         custom_id="text_input_response",
    #         min_length=1,
    #         max_length=3,
    #         )

    #     modal = interactions.Modal(
    #         title="Application Form",
    #         custom_id="mod_app_form",
    #         components=[tI],
    #     )

    #     await ctx.popup(modal)


    # @interactions.extension_command(
    #     name="button_test",
    #     description="This is the first command I made!",
    #     scope=271639846307627008,
    # )
    # async def button_test(self, ctx):
    #     button = interactions.Button(
    #     style=interactions.ButtonStyle.PRIMARY,
    #     label="hello world!",
    #     custom_id="hello")
    #     await ctx.send("testing", components=button)

    # @interactions.extension_component("hello")
    # async def button_response(self, ctx):
    #     await ctx.send("You clicked the Button :O", ephemeral=True)

    # @interactions.extension_modal("mod_app_form")
    # async def modal_response(self, ctx, response: str):
    #     await ctx.send(f"You wrote: {response}", ephemeral=True)

def setup(client):
    MainUtility(client)


