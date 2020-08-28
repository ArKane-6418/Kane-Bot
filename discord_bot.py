import discord
import time
import asyncio
import json
import datetime
import os
from discord.ext import commands
from discord.utils import get

print(os.listdir())

joined = 0

bot = commands.Bot(command_prefix="!")

with open("resources.json", "r") as f:
    bot.config = json.load(f)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready.")


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send(f"Hello there, {ctx.author.mention}.")


# Voice Channel commands

@bot.command(name="join")
async def join(ctx):
    print("Joining!")
    vc = ctx.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(vc)
    else:
        await vc.connect()
        print("Joined!")
        await ctx.send(f"Joined {vc}")


@bot.command(name="leave")
async def leave(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send(f"Left {ctx.author.voice.channel}")


@bot.command(name="vc_help")
async def vc_help(ctx):

    vc_commands = []
    vc_commands.append("\n**!join** - Brings bot to the voice channel you are in")
    vc_commands.append("\n**!leave** - Disconnects bot from voice channel")
    vc_commands.append("\n**!p <youtube_url>** - Use this command when the bot first joins the VC to play <youtube_url>")
    vc_commands.append("\n**!q <youtube_url>** - Queues any subsequent songs")
    vc_commands.append("\n**!pause** - Pauses current song")
    vc_commands.append("\n**!resume** - Resumes current song")
    vc_commands.append("\n**!next** - Skips to next song in queue")
    vc_commands.append("\n**!stop** - Stops the song and resets the entire queue")

    embed = discord.Embed(colour=ctx.author.colour,
                          timestamp=datetime.datetime.utcnow(), title="VC Commands",
                          description=" ".join(vc_commands))

    embed.set_footer(text=f"Requested by {ctx.author}",
                     icon_url=ctx.author.avatar_url)
    embed.set_author(name="Help", icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)


# async def update_stats():
#     await bot.wait_until_ready()
#     global joined
#
#     while not bot.is_closed():
#         try:
#             with open("stats.txt", "a") as f:
#                 f.write(
#                     f"Time: {int(time.time())}, , Members Joined: {joined}\n")
#
#             joined = 0
#
#             await asyncio.sleep(3600)
#         except Exception as e:
#             print(e)
#             await asyncio.sleep(3600)


@bot.event
async def on_member_update(before, after):
    n = after.nick
    if n:
        if n.lower().count("ArKane") > 0:
            last = before.nick
            if last:
                await after.edit(nickname=last)
            else:
                await after.edit(nickname="No.")


@bot.event
async def on_member_join(member):
    global joined
    joined += 1
    channel = bot.get_channel(bot.config["welcomeCh"][str(member.guild.id)])
    await channel.send(bot.config["welcomeMsg"][str(member.guild.id)].format(
        member.display_name))
    await channel.send(
        f"If you have any questions, please ask {member.guild.owner.display_name}.")
    await channel.send(f"""Current # of members is {joined}""")


@bot.event
async def on_member_remove(member):
    global joined
    joined -= 1
    channel = bot.get_channel(bot.config["logsCh"][str(member.guild.id)])
    await channel.send(f"""Sorry to see you go, {member.display_name}""")


def channel_check():
    async def pred(ctx):
        return ctx.message.channel.id == 583872784497770499
    return commands.check(pred)


@bot.command(name="userinfo")
async def userinfo(ctx, member: discord.Member = None):
    member = ctx.author if not member else member

    roles = [role for role in member.roles if role.name != "@everyone"]

    create_date = member.created_at.strftime("%a, %B %#d, %Y, %I:%M:%S %p UTC")
    join_date = member.joined_at.strftime("%a, %B %#d, %Y, %I:%M:%S %p UTC")
    values = []
    values.append(f"\n**ID Number**: {member.id}")
    values.append(f"\n**Display name**: {member.display_name}")
    values.append(f"\n**Created at**: {create_date}")
    values.append(f"\n**Joined at**: {join_date}")
    values.append(f"\n**Roles ({len(roles)})**: " + " ".join([role.mention for role in roles]))
    values.append(f"\n**Bot?**: {member.bot}")

    embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at,
                          description=" ".join(values))
    embed.set_author(name=f"User Info - {member}", icon_url=member.avatar_url)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)


@bot.command(name="commands")
async def command_info(ctx):
    embedded = discord.Embed(title="Help:",
                             description="Useful commands")
    embedded.add_field(name="!users",
                       value="Prints the number of users.")
    embedded.add_field(name="!Zura", value="Mirai zura!")
    embedded.add_field(name="!Ruby", value="Ganbaruby!")
    embedded.add_field(name="!Chun Chun", value="Birb")
    embedded.add_field(name="!Yoshiko", value="Datenshi")
    embedded.add_field(name="!Yohane", value="True Fallen Angel")
    embedded.add_field(name="!You", value="o7")
    embedded.add_field(name="!Kanan", value="Hagu")
    embedded.add_field(name="!Rin", value="Nya!")
    embedded.add_field(name="!Chika", value="Kiseki dayo!")
    embedded.add_field(name="!Mari", value="It's joke!")
    embedded.add_field(name="!aqours", value="0 to 1!")
    await ctx.send(content=None, embed=embedded)


@bot.command(name="addrole")
@channel_check()
@commands.has_permissions(manage_roles=True)
async def add_role(ctx, *, role: discord.Role):
    member = ctx.author
    await member.add_roles(role)
    embed = discord.Embed(colour=discord.Colour.dark_blue(),
                          description=f"Successfully gave {role.mention} to: `{member.display_name}`",
                          timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=f"Requested by {ctx.author}",
                     icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name="removerole", aliases=["remove"])
@commands.has_permissions(manage_roles=True)
@channel_check()
async def remove_role(ctx, *, role: discord.Role):
    member = ctx.author
    await member.remove_roles(role)
    embed = discord.Embed(colour=discord.Colour.dark_blue(),
                          description=f"Successfully removed {role.mention} from: `{member.display_name}`",
                          timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=f"Requested by {ctx.author}",
                     icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name="rolecolour", aliases=["rolecolor"])
@channel_check()
@commands.has_permissions(manage_roles=True)
async def role_colour(ctx, colour: discord.Colour, *, role: discord.Role):
    role_mention = role.mention

    await role.edit(color=colour)
    embed = discord.Embed(colour=discord.Colour.dark_blue(), description= f"Successfully changed the colour of {role_mention} to `{colour}`",
                          timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=f"Requested by {ctx.author}",
                     icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name="createrole")
@commands.has_permissions(manage_roles=True)
@channel_check()
async def create_role(ctx, *, role_name: str):

    await ctx.guild.create_role(name=role_name)
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    embed = discord.Embed(colour=discord.Colour.dark_blue(), description= f"Successfully created {role.mention}",
                          timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=f"Requested by {ctx.author}",
                     icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name="deleterole", aliases=["role"])
@commands.has_permissions(manage_roles=True)
@channel_check()
async def delete_role(ctx, *, role: discord.Role):

    embed = discord.Embed(colour=discord.Colour.dark_blue(), description= f"Successfully deleted {role.mention}",
                          timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=f"Requested by {ctx.author}",
                     icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)
    await role.delete()


@bot.command(name="status")
async def status(ctx):
    current_guild = bot.get_guild(bot.config["serverID"][str(ctx.message.guild.id)])
    online = 0
    idle = 0
    offline = 0
    for m in current_guild.members:
        if str(m.status) == "online":
            online += 1
        if str(m.status) == "offline":
            offline += 1
        else:
            idle += 1

    await ctx.send(
        f"```Online: {online}\nIdle: {idle}\nOffline: {offline}```")
# bot.loop.create_task(update_stats())
file_object = open("token.txt", "r")
bot.run(file_object.read().strip())
