import discord, os, datetime, json, requests, yaml, time, asyncio
from discord.ext import commands
from discord.utils import get

path = "/home/pi/Desktop/bot/"

f = open(path + "config.yml", "r")
config = yaml.load(f)
f.close()

client = commands.Bot(command_prefix=config["prefix"])
# client.remove_command("help")


async def log(msg):
    format_time = datetime.datetime.now().strftime("[%m/%d/%Y-%H:%M:%S]")
    format_msg = format_time + " " + msg
    channel = client.get_channel(config["logChannel"])
    await channel.send(format_msg)


@client.event
async def on_ready():
    print("READY")
    await log("Successful Logged In")

@client.command(pass_context=True)
async def chunk(ctx):
    embed = discord/Embed(title="Cai is fat!")
    await ctx.channel.message(embed=embed)


##@client.event
##async def on_command_error(ctx, error):
##    if isinstance(error, commands.CheckFailure):
##        embed = discord.Embed(title="You do not have permission to preform that commands.", color=0x7eded2)
##        msg = await ctx.message.channel.send(embed=embed)
##        time.sleep(5)
##        await ctx.message.channel.delete_messages([ctx.message, msg])
##    elif isinstance(error, commands.CommandNotFound):
##        embed = discord.Embed(title="You entered an invalid commands.", color=0x7eded2)
##        msg = await ctx.message.channel.send(embed=embed)
##        await asyncio.sleep(5)
##        await ctx.message.channel.delete_messages([ctx.message, msg])
        
@commands.has_any_role("Admin", "Moderator")
@client.command(pass_context=True)
async def purge(ctx, lim=100):
    try:
        deleted = await ctx.message.channel.purge(limit=lim)
        embed = discord.Embed(title="{} messages have been deleted!".format(len(deleted)), color=0x7eded2)
        msg = await ctx.message.channel.send(embed=embed)
        await log("{0.message.author.name} deleted {1} message/s from {0.message.channel.name}.".format(ctx, len(deleted)))
    except:
        embed = discord.Embed(title="You can only delete messages younger that 14 days.", color=0x7eded2)
        msg = await ctx.message.channel.send(embed=embed)
    await asyncio.sleep(5)
    await ctx.message.channel.delete_messages([ctx.message, msg])


@client.command(pass_context=True)
async def addrole(ctx, roleName):
    try:
        role = roleName.lower()
        role = discord.utils.get(ctx.message.guild.roles, name=role)
        await ctx.message.author.add_roles(role)
        embed = discord.Embed(title="The role has been added.", color=0x7eded2)
        msg = await ctx.message.channel.send(embed=embed)
        await log("{} gave themselves the role {}.".format(ctx.message.author.name, roleName))
    except:
        embed = discord.Embed(title="That role either doesn't exist or is unobtainable.", color=0x7eded2)
        msg = await ctx.message.channel.send(embed=embed)
    await asyncio.sleep(5)
    await ctx.message.channel.delete_messages([ctx.message, msg])
@client.command(pass_context=True)
async def removerole(ctx, roleName):
    try:
        role = roleName.lower()
        role = discord.utils.get(ctx.message.guild.roles, name=role)
        await ctx.message.author.remove_roles(role)
        embed = discord.Embed(title="The role has been removed.", color=0x7eded2)
        msg = await ctx.message.channel.send(embed=embed)
        await log("{} remove  their {} role.".format(ctx.message.author.name, roleName))
    except:
        embed = discord.Embed(title="You do not have this role, or you cannot remove it.", color=0x7eded2)
        msg = await ctx.message.channel.send(embed=embed)
    await asyncio.sleep(5)
    await ctx.message.channel.delete_messages([ctx.message, msg])


@client.group(aliases=[], pass_context=True)
async def suggest(ctx):
    if ctx.invoked_subcommand is None:
        msg = await ctx.message.channel.send("Invalid subcommand")
        await asyncio.sleep(5)
        await ctx.message.channel.delete_messages([ctx.message, msg])

@suggest.command(pass_context=True)
async def add(ctx, *description):
    suggestionID = config["amtSuggestions"] + 1
    config["amtSuggestions"] = suggestionID
    f = open(path + "config.yml","w")
    yaml.dump(config, f, default_flow_style=False)
    f.close()

    channel = client.get_channel(config["suggestionChannel"])
    embed = discord.Embed(title="Suggestion by **{}**".format(ctx.message.author.name), color=0xffff24)
    embed.add_field(name="Status: Open", value="Description: *{}*".format(" ".join(description)))
    embed.set_footer(text="Suggestion ID: {}".format(suggestionID))
    f=open(path + "suggestions/{}.yml".format(suggestionID), "w")
    message = await channel.send(embed=embed)

    await message.add_reaction("✅")
    await message.add_reaction("❌")
    
    suggestionInfo = {"suggestionMessageID": int(message.id), "suggester": ctx.message.author.name, "suggestionID": suggestionID, "description": " ".join(description)}
    yaml.dump(suggestionInfo, f, default_flow_style=False)
    f.close()
    embed= discord.Embed(title="You suggestion has been submitetd.", color=0x7eded2)
    msg = await ctx.message.channel.send(embed=embed)
    await asyncio.sleep(5)
    await ctx.message.channel.delete_messages([ctx.message, msg])

@commands.has_any_role("Admin")
@suggest.command(aliases=["response", "answer"], pass_context=True)
async def respond(ctx, suggestionID, action):
    action = action.lower()
    f=open(path + "suggestions/{}.yml".format(suggestionID))
    file = yaml.load(f)
    f=open(path + "config.yml")
    config=yaml.load(f)
    f.close()
    channel = client.get_channel(config["suggestionChannel"])
    message = await channel.fetch_message(file["suggestionMessageID"])

    if action == "accept":
        embed = discord.Embed(title="Suggestion by **{}**".format(file["suggester"]), color=0x00ff00)
        embed.add_field(name="Status: Accepted", value="Description: *{}*".format(file["description"]))
        embed.set_footer(text="Suggestion ID: {}".format(suggestionID))
        await message.edit(embed=embed)
        embed = discord.Embed(title="Suggestion Accepted.", color=0x7eded2)
        response = await ctx.message.channel.send(embed=embed)
    elif action == "deny" or action == "reject":
        embed = discord.Embed(title="Suggestion by **{}**".format(file["suggester"]), color=0xff0000)
        embed.add_field(name="Status: Rejected", value="Description: *{}*".format(file["description"]))
        embed.set_footer(text="Suggestion ID: {}".format(suggestionID))
        await message.edit(embed=embed)
        embed = discord.Embed(title="Suggestion Rejected.", color=0x7eded2)
        response = await ctx.message.channel.send(embed=embed)
    elif action == "open":
        embed = discord.Embed(title="Suggestion by **{}**".format(file["suggester"]), color=0xffff24)
        embed.add_field(name="Status: Open", value="Description: *{}*".format(file["description"]))
        embed.set_footer(text="Suggestion ID: {}".format(suggestionID))
        await message.edit(embed=embed)
        embed = discord.Embed(title="Suggestion Re-opened.", color=0x7eded2)
        response = await ctx.message.channel.send(embed=embed)
    else:
        response = ctx.message.channel.send(embed=discord.Embed(title="Either accept, reject or open the suggestion", color=0x7eded2))
    await asyncio.sleep(5)
    await ctx.message.channel.delete_messages([ctx.message, response])

@client.group(pass_context=True, aliases=["wynncraft", "Wynncraft", "WYNNCRAFRT", "Wynn", "WYNN"])
async def wynn(ctx):
    if ctx.invoked_subcommand is None:
        msg = await ctx.message.channel.send("You need to enter a valid subcommand.")
        await asyncio.sleep(5)
        await ctx.message.channel.delete_messages([ctx.message, msg])

@wynn.command(pass_context=True)
async def stats(ctx, player):
    try:
        response = requests.get("https://api.wynncraft.com/v2/player/{}/stats".format(player))
        data = json.loads(response.text)
        data = data["data"][0]
        embed = discord.Embed(title="Wynncraft Stats".format(ctx.message.author.name), description="play.wynncraft.net.",color=0x7eded2)
        embed.set_thumbnail(url="https://minotar.net/avatar/{}/100.png".format(player))
        embed.add_field(name="Player", value=data["username"], inline=True)

        rank = data["meta"]["tag"]["value"]
        if rank == None:
            rank = "Player"
        if data["guild"]["name"] == None:
            guild = "None"
        else:
            guild = str(data["guild"]["rank"]) + " of " + data["guild"]["name"].capitalize()

        embed.add_field(name="Rank", value=rank, inline=True)
        embed.add_field(name="Guild", value=guild, inline=True)
        embed.add_field(name="Playtime", value=str(round(data["meta"]["playtime"] / 60 * 4.7)) + " hours", inline=True)

        if data["meta"]["location"]["online"] == True:
            loc = "{} is currently online in {}.".format(player, data["meta"]["location"]["server"])
        else:
            loc = "{} is currently offline.".format(player)
        embed.set_footer(text=loc)
        msg = await ctx.message.channel.send(embed=embed)

    except Exception as x:
        msg = await ctx.message.channel.send("Something went wrong. Please make sure you entered the correct username, ensure you have the correct capitalization.")
        #raise x
    await asyncio.sleep(50)
    await ctx.message.channel.delete_messages([ctx.message, message])

@wynn.command(pass_context=True)
async def guide(ctx, guide, sub1=None, sub2=None):
    guide = guide.lower()
    if guide == "add":
        f = open(path + "wynnguides.json", "r")
        data = json.load(f)
        exists = False
        for key, value in data.items():
            if key == sub1:
                embed = discord.Embed(title="A guide with that name already exists",color=0x7eded2)
                msg = await ctx.message.channel.send(embed=embed)
                exists = True
            else:
                pass
        if exists == False:
            data[sub1] = sub2
            f = open(path + "wynnguides.json", "w")
            json.dump(data, f, indent=4)
            f.close()
            embed = discord.Embed(title="Guide Successfully Added",color=0x7eded2)
            msg = await ctx.message.channel.send(embed=embed)
            thetime = 5

    elif guide == "list":
        f = open(path + "wynnguides.json", "r")
        data = json.load(f)
        listofguides = ""
        for key, value in data.items():
            listofguides += f"{key}\n"
        msg = await ctx.message.channel.send(listofguides)
        thetime = 20
    else:
        f = open(path + "wynnguides.json", "r")
        data = json.load(f)
        try:
            msg = await ctx.message.channel.send(data[guide])
        except:
            embed = discord.Embed(title="That guide doesnt exists", description="Try adding it with +wynn guide add [title] [content/link]", color=0x7eded2)
            msg = await ctx.message.channel.send(embed=embed)
        thetime = 25
    await asyncio.sleep(thetime)
    await ctx.message.channel.delete_messages([ctx.message, msg])



async def membercount():
    await client.wait_until_ready()
    channel = client.get_channel(642369613002178572)
    while True:
        welchannel = client.get_channel(642403866406551552)
        await welchannel.edit(name=f"Members: {len(set(client.get_all_members()))}")
        print(len(set(client.get_all_members())))
        await asyncio.sleep(5)

client.loop.create_task(membercount())


client.run('MjU5NzgxNTMyODQxOTM0ODQ4.XbnNtw.2Ng8ohNk7W2kyusZca30UwwmPB0')
