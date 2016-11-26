import discord
from discord.ext import commands
from utils.dataIO import fileIO
from utils import checks
import asyncio
import os
import time
import sys

token = '' #Bot Token.

formatter = commands.HelpFormatter(show_check_failure=False)

description = '''This bot is designed for the use in all servers.
Bot still in BETA (1.0)'''
bot = commands.Bot(command_prefix='?', formatter=formatter,
                   description=description, pm_help=None)

#############################################

savetofile = fileIO("data/padid/padid.json", "load")

@bot.event
async def on_ready():
    users = str(len(set(bot.get_all_members())))
    servers = str(len(bot.servers))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print("{} servers".format(servers))
    print("{} users".format(users))


####Creates pad command set########################################################################

@bot.group(name="pad", pass_context=True)
async def _pad(ctx):
    """https://discord.gg/0jCMczFXa52NDh9P"""
    if ctx.invoked_subcommand is None:
        await send_cmd_help(ctx)

####Function for saving player IDs into JSON#######################################################
@_pad.command(pass_context=True, no_pm=False)
async def id(ctx):
    """Saves your PAD ID.
    Example usage: ?pad id 334980359"""
    user = ctx.message.author
    pid = ctx.message.content.split()
    if len(pid) != 3:
        await bot.say("""```    Saves your PAD ID.
    Example usage: ?pad id 334980359```""")
    else:
        if pid[2].isdigit():
            if 99999999 < int(pid[2]) < 999999999:
                if pid[2].startswith("3"):
                    savetofile[user.id] = {"name" : user.name, "id" : pid[2], "team1" : "", "team2" : "", "team3" : "", "padherder" : "", "null" : ""}
                    fileIO("data/padid/padid.json", "save", savetofile)
                    await bot.say("{} Saved. Your ID is now {}. All Leads have been cleared. Padherder cleared.".format(user.mention, check_id(user.id)))
                else:
                    await bot.say("NA only atm.")
            else:
                await bot.say("no.")
        else:
            await bot.say("That is not an ID!")

####Save Padherder info###########################################################################
##################################################################################################

@_pad.command(pass_context=True, no_pm=False)
async def box(ctx):
    """Saves your Padherder.
    Example usage: ?pad box [PADHERDER]"""
    user = ctx.message.author
    oldid = check_id(user.id)
    oldteam1 = check_team1(user.id)
    oldteam2 = check_team2(user.id)
    oldteam3 = check_team3(user.id)
    pod = ctx.message.content.split(' ')
    padurl = pod[2].split('/')
    if account_check(user.id):
        if len(pod) != 3:
            await bot.say("""```    Saves your PAD ID.
    Example usage: ?pad box NepNep OR ?pad box https://www.padherder.com/user/NepNep/monsters/```""")
        else:
            if pod[2].startswith("http"):
                realpadherder = "https://www.padherder.com/user/" + padurl[4]
                savetofile[user.id] = {"name" : user.name, "id" : oldid, "team1" : oldteam1, "team2" : oldteam2, "team3" : oldteam3, "padherder" : realpadherder, "null" : ""}
                fileIO("data/padid/padid.json", "save", savetofile)
                await bot.say("Saved.")
            elif pod[2].startswith("www.padherder"):
                realpadherder = "https://www.padherder.com/user/" + padurl[2]
                savetofile[user.id] = {"name" : user.name, "id" : oldid, "team1" : oldteam1, "team2" : oldteam2, "team3" : oldteam3, "padherder" : realpadherder, "null" : ""}
                fileIO("data/padid/padid.json", "save", savetofile)
                await bot.say("Saved.")
            else:
                realpadherder = "https://www.padherder.com/user/" + pod[2]
                savetofile[user.id] = {"name" : user.name, "id" : oldid, "team1" : oldteam1, "team2" : oldteam2, "team3" : oldteam3, "padherder" : pod[2], "null" : ""}
                fileIO("data/padid/padid.json", "save", savetofile)
                await bot.say("Saved.")

####Reads JSON for target ID######################################################################

@_pad.command(pass_context=True)
async def user(ctx, user : discord.Member=None):
    """Shows PAD ID ,leads, and Padherder of user.
    Defaults to yours."""
    if not user:
        user = ctx.message.author
        if account_check(user.id):
            await bot.say("{} Your Puzzle & Dragons ID is: ```py\n{}```\n{} {} {} \n{}".format(user.mention, check_id(user.id), check_team1(user.id), check_team2(user.id), check_team3(user.id), check_padherder(user.id)))
        else:
            await bot.say("{} You don't have your Puzzle & Dragons ID saved. used `!pad add [YOUR ID]` to register.".format(user.mention, check_id(user.id)))
    else:
        if account_check(user.id):
            balance = check_id(user.id)
            await bot.say("{}'s Puzzle & Dragons ID is ```py\n{}```\n{} {} {} \n{}".format(user.name, balance, check_team1(user.id), check_team2(user.id), check_team3(user.id), check_padherder(user.id)))
        else:
            await bot.say("That user has no Puzzle & Dragons account.")

####Print all users##############################################################################

@_pad.command(pass_context=True)
async def all():
    """Lists all saved PAD IDs."""
    padlist = ""
    for id in savetofile:
        padlist += (savetofile[id]["id"] + "    " +savetofile[id]["name"] + "\n")
    if padlist:
        await bot.say("```py\n"+padlist+"```")

####Saves Teams###################################################################################

@_pad.command(pass_context=True, no_pm=False)
async def leads(ctx):
    """Saves your most used PAD Teams. Up to 3 teams!
	Example usage: ?pad leads Yomidra XiangMei Idunn&Idunna"""
    user = ctx.message.author
    pteam = ctx.message.content.split()
    currentid = check_id(user.id)
    currentpadherder = check_padherder(user.id)
    if account_check(user.id):
        if len(pteam) == 2:
            await bot.say("```Wrong! Type your teams like: ?pad teams [Team 1] [Team 2] [Team 3]```")

        elif len(pteam) == 3:
            savetofile[user.id] = {"name" : user.name, "id" : currentid, "team1" : pteam[2], "team2" : "", "team3" : "", "padherder" : currentpadherder, "null" : ""}
            fileIO("data/padid/padid.json", "save", savetofile)
            await bot.say("{} Saved. Your top team is {}.".format(user.mention, check_team1(user.id)))

        elif len(pteam) == 4:
            savetofile[user.id] = {"name" : user.name, "id" : currentid, "team1" : pteam[2], "team2" : pteam[3], "team3" : "", "padherder" : currentpadherder, "null" : ""}
            fileIO("data/padid/padid.json", "save", savetofile)
            await bot.say("{} Saved. Your top 2 teams are {}, and {}.".format(user.mention, check_team1(user.id), check_team2(user.id)))

        elif len(pteam) == 5:
            savetofile[user.id] = {"name" : user.name, "id" : currentid, "team1" : pteam[2], "team2" : pteam[3], "team3" : pteam[4], "padherder" : currentpadherder, "null" : ""}
            fileIO("data/padid/padid.json", "save", savetofile)
            await bot.say("{} Saved. Your top 3 teams are {}, {}, and {}.".format(user.mention, check_team1(user.id), check_team2(user.id), check_team3(user.id)))

        else:
            await bot.say("```Wrong! Type your teams like: ?pad teams [Team 1] [Team 2] [Team 3]. Don't use spaces in team names!```")
    else:
        await bot.say("You dont have your ID saved! Do it with ?pad id")

################################################################################################
####ADMIN STUFF#################################################################################
################################################################################################
@bot.command()
@checks.is_owner()
async def restart():
    """Restarts Pandora. NepNep Only."""
    await bot.say("Restarting.")
    await bot.logout()

@bot.command()
@checks.is_owner()
async def stats():
    """Bot stats. NepNep Only."""
    users = str(len(set(bot.get_all_members())))
    servers = str(len(bot.servers))
    plot = 1
    for id in savetofile:
        plot = 1 + plot
    await bot.say("""```    Servers: {}
    Users: {}
    Saved Users: {}```""".format(servers, users, str(plot - 1)))

@bot.command(pass_context=True)
@checks.is_owner()
async def servers(ctx):
    """Lists servers"""
    owner = ctx.message.author
    servers = list(bot.servers)
    server_list = {}
    msg = ""
    for i in range(0, len(servers)):
        server_list[str(i)] = servers[i]
        msg += "{}: {}\n".format(str(i+1), servers[i].name)
    msg += ""
    await bot.say(msg)

##################################################################################################
##################################################################################################
####Checks for existing data######################################################################

def account_check(id):
    if id in savetofile:
        return True
    else:
        return False

def check_id(id):
    if account_check(id):
        return savetofile[id]["id"]
    else:
        return False

def check_team1(id):
    if account_check(id):
        return savetofile[id]["team1"]
    else:
        return False

def check_team2(id):
    if account_check(id):
        return savetofile[id]["team2"]
    else:
        return False

def check_team3(id):
    if account_check(id):
        return savetofile[id]["team3"]
    else:
        return False

def check_padherder(id):
    if account_check(id):
        return savetofile[id]["padherder"]
    else:
        return False


####Some stuff####################################################################################
@bot.event
async def on_command(command, ctx):
    pass

@bot.event
async def on_command(command, ctx):
    pass

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.channel, 
            "That command is disabled.")
    elif isinstance(error, commands.CommandNotFound):
        pass

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)


def check_folders():
    if not os.path.exists("data/padid"):
        print("Creating data/padid folder...")
        os.makedirs("data/padid")

def check_files():
    f = "data/padid/padid.json"
    if not fileIO(f, "check"):
        print("Creating empty padid.json...")
        fileIO(f, "save", {})

####More stuff####################################################################################

def main():
    global settings
    global checks


    check_folders()
    check_files()


if __name__ == "__main__":
    main()


bot.run(token)
