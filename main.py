############################################################## M O D U L E ########################################################################

import discord
import sys
import traceback
import aiohttp
import random
import asyncio
import datetime
import os
import urlextract
import requests
from discord import Embed
import json
import subprocess
import platform
import psutil
from termcolor import colored
import time 
from discord.ext import commands
from colorama import init, Fore, Back, Style
import whois
from io import BytesIO
from PIL import Image
import logging

############################################################## V A R I A B L E ####################################################################

init()

with open('settings/data.json', 'r') as f:
    data = json.load(f)
    
token = data['token']
webhookerror = data['webhookerror']
webhooklogs = data['webhooklogs']
salon_id = data['salon_id']
compte_id = data['compte_id']

bot = commands.Bot(command_prefix="&", self_bot=True)
bot.remove_command('help')
anti_group_enabled = False
antifriend_active = False
js_process = None

############################################################## E V E N T S ########################################################################

async def send_error_log(error_msg):
  headers = {"Content-Type": "application/json"}
  data = {"content": f"<@{compte_id}> Error occurred:```{error_msg}```"}

  async with aiohttp.ClientSession(headers=headers) as session:
    async with session.post(webhookerror, json=data):
      pass

@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if message.guild:
                server_name = message.guild.name
                channel_name = message.channel.name if isinstance(message.channel, discord.TextChannel) else "Direct Message"
            else:
                server_name = "Direct Message"
                channel_name = "Direct Message"
 
            embed = Embed(
                title="New image",
                description=
                f"Posted by: {message.author.name}#{message.author.discriminator} ({message.author.id})\n"
                f"Posted at: {message.created_at}\n"
                f"Server: {server_name}\n"
                f"Channel: {channel_name}",
                color=0x00ff00)
            embed.set_image(url=attachment.url)
            data = {"embeds": [embed.to_dict()]}
            requests.post(webhooklogs, json=data)
 
            with open("logs/url.txt", "a") as f:
                f.write(attachment.url + "\n")
 
    extractor = urlextract.URLExtract()
    urls = extractor.find_urls(message.content)
    if urls:
        for url in urls:
            if message.guild:
                server_name = message.guild.name
                channel_name = message.channel.name if isinstance(message.channel, discord.TextChannel) else "Direct Message"
            else:
                server_name = "Direct Message"
                channel_name = "Direct Message"
 
            embed = Embed(
                title="New URL",
                description=
                f"Posted by: {message.author.name}#{message.author.discriminator} ({message.author.id})\n"
                f"Posted at: {message.created_at}\n"
                f"Server: {server_name}\n"
                f"Channel: {channel_name}\n"
                f"URL: {url}",
                color=0x00ff00)
            data = {"embeds": [embed.to_dict()]}
            requests.post(webhooklogs, json=data)
 
            with open("logs/url.txt", "a") as f:
                f.write(url + "\n")
 
    await bot.process_commands(message)
 
 
@bot.event
async def on_message_edit(before, after):
  if before.content != after.content:
    embed = Embed(title="Message edited", color=0xFFA500)
    embed.add_field(name="Before", value=before.content, inline=False)
    embed.add_field(name="After", value=after.content, inline=False)
    embed.set_author(
      name=f"{before.author.name}#{before.author.discriminator}",
      icon_url=before.author.avatar)
    embed.set_footer(text=f"Edited at: {after.edited_at}")
    if before.guild:
      embed.add_field(name="Server", value=before.guild.name, inline=True)
      embed.add_field(name="Channel", value=before.channel.name, inline=True)
    else:
      embed.add_field(name="Channel", value="DM", inline=True)
    data = {"embeds": [embed.to_dict()]}
    requests.post(webhooklogs, json=data)
 
 
@bot.event
async def on_message_delete(message):
  if message.attachments:
    for attachment in message.attachments:
      embed = Embed(
        title="Deleted message",
        description=f"The deleted message contained an image: {attachment.url}",
        color=0xFF5733,
      )
      embed.set_author(
        name=
        f"{message.author.name}#{message.author.discriminator} ({message.author.id})",
        icon_url=message.author.avatar,
      )
      embed.set_footer(text=f"Deleted at: {message.created_at}")
      if message.guild:
        embed.add_field(name="Server", value=message.guild.name, inline=True)
        embed.add_field(name="Channel",
                        value=message.channel.name,
                        inline=True)
      else:
        embed.add_field(name="Server", value="DM", inline=True)
 
      payload = {"embeds": [embed.to_dict()]}
 
      headers = {"Content-Type": "application/json"}
 
      requests.post(webhooklogs, data=json.dumps(payload), headers=headers)
  elif message.content:
    embed = Embed(
      title="Deleted message",
      description=f"The deleted message was: {message.content}",
      color=0xFF5733,
    )
    embed.set_author(
      name=
      f"{message.author.name}#{message.author.discriminator} ({message.author.id})",
      icon_url=message.author.avatar,
    )
    embed.set_footer(text=f"Deleted at: {message.created_at}")
    if message.guild:
      embed.add_field(name="Server", value=message.guild.name, inline=True)
      embed.add_field(name="Channel", value=message.channel.name, inline=True)
    else:
      embed.add_field(name="Server", value="DM", inline=True)
 
    payload = {"embeds": [embed.to_dict()]}
 
    headers = {"Content-Type": "application/json"}
 
    requests.post(webhooklogs, data=json.dumps(payload), headers=headers)
  else:
    embed = Embed(
      title="Deleted message",
      description="The deleted message contained no text or attachments.",
      color=0xFF5733,
    )
    embed.set_author(
      name=
      f"{message.author.name}#{message.author.discriminator} ({message.author.id})",
      icon_url=message.author.avatar,
    )
    embed.set_footer(text=f"Deleted at: {message.created_at}")
    if message.guild:
      embed.add_field(name="Server", value=message.guild.name, inline=True)
      embed.add_field(name="Channel", value=message.channel.name, inline=True)
    else:
      embed.add_field(name="Server", value="DM", inline=True)
 
    payload = {"embeds": [embed.to_dict()]}
 
    headers = {"Content-Type": "application/json"}
 
    requests.post(webhooklogs, data=json.dumps(payload), headers=headers)

async def on_connect():
 @bot.event
 async def on_ready():
   await bot.change_presence(activity=discord.Streaming(name="Core Project", url="https://www.twitch.tv/@discord"))
   os.system('cls' if os.name == 'nt' else 'clear')
   acc_id = bot.get_user(int(compte_id))
   avatar_url = acc_id.avatar
   data = {"username": bot.user.name,"pfp_link": str(avatar_url)}
   r = requests.post("https://core-client-api.xcoreproject.repl.co/api/notifier", json=data)
   print(Fore.YELLOW + 'User: ' + Fore.RESET + bot.user.name, end='\n\n')
   print(Style.BRIGHT + Fore.GREEN + "The on_connect event fired successfully, good use!" + Style.RESET_ALL)

async def main():
 await on_connect()
 print(Style.BRIGHT + Fore.MAGENTA + "Starting the app." + Style.RESET_ALL)
 print(Style.BRIGHT + Fore.MAGENTA + "The application is running. Please wait.." + Style.RESET_ALL)
 
 animation_texte = "|/-\\"
 for i in range(10):
   time.sleep(0.1)
   sys.stdout.write("\r" + "Loading " + animation_texte[i % len(animation_texte)])
   sys.stdout.flush()
   
asyncio.run(main())

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.send("Command not found. Please check the syntax.")

############################################################## C O M M A N D S ####################################################################

############################################################## S T A T U S ########################################################################

@bot.command(aliases=["streaming", "game", "listen", "watch"])
async def setactivity(ctx, act_type: str, *, message: str):
    await ctx.message.delete()
    if not message:
        await ctx.send(
            f'[ERROR]: Invalid input! Command: {bot.command_prefix}{act_type} <message>'
        )
        return
    activity_type = {
        "streaming": discord.Streaming,
        "game": discord.Game,
        "listen": lambda x: discord.Activity(type=discord.ActivityType.listening, name=x),
        "watch": lambda x: discord.Activity(type=discord.ActivityType.watching, name=x),
    }.get(act_type.lower())
    if activity_type is None:
        await ctx.send(
            f'[❌]: ```Invalid activity type! Available types: streaming, game, listen, watch```'
        )
        return
    if act_type.lower() == "streaming":
        url = f"https://www.twitch.tv/discord"
        await bot.change_presence(activity=activity_type(name=message, url=url), status=discord.Status.online)
    else:
        await bot.change_presence(activity=activity_type(message), status=discord.Status.online)



@bot.command(aliases=[
  "stopstreaming", "stopstatus", "stoplistening", "stopplaying", "stopwatching"
])
async def stopactivity(ctx):
  await ctx.message.delete()
  await bot.change_presence(activity=None, status=discord.Status.dnd)
    
  
############################################################## P I N G ###########################################################################  
    
@bot.command()
async def ping(ctx):
    await ctx.message.delete()
    latency = bot.latency * 1000 # Convert to milliseconds
    message = f"My latency is {latency:.2f}ms"
    await ctx.send(message)

@bot.command()
async def network(ctx):
    await ctx.message.delete()
    
    github = "https://github.com/xCoreProject/CoreClient/"
    discord_server = "https://discord.gg/M4DeuABSKz"
    
    response = f"`Core Network` :\n`Github:` {github}\n\n`Support:` {discord_server}"
    await ctx.send(response)

############################################################## H E L P ############################################################################


@bot.command()
async def help(ctx):
    await ctx.message.delete()
    help_text = '''>>> ```       C O R E - P R O J Ǝ C T | V1       ```
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

>`By Yanzu & Muzu & Ayzu` **with** :heart:

***NO SKID PLS THX :)***
**Prefix : &**
`network` ㇱ

`status` 
`clean` 
`guild` 
`account` 
`utils` 

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1       ```'''
    await ctx.send(help_text)

@bot.command()
async def status(ctx):
    await ctx.message.delete()
    help_text = '''>>> `=================== S T A T U S ㊔ ====================`
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

**Prefix : &**

||RPC SOON ON V2||

`setactivity {args} [message]` => `Load custom status`
`[+]`  `&setactivity streaming Core Self`

`>stopactivity` => `Stop custom status`

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1       ```'''
    await ctx.send(help_text)

@bot.command()
async def clean(ctx):
    await ctx.message.delete()
    help_text = '''>>> `=================== C L E A R ㊑ ====================`
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

**Prefix : &**

`cleardm` => `Remove all DMs from your account`
`clears` => `Remove all channels from your server (Useful in case of raid)`
`clear_logs` => `Clear the logs`

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1       ```'''
    await ctx.send(help_text)
    
@bot.command()
async def guild(ctx):
    await ctx.message.delete()
    help_text = '''>>> `=================== G U I L D ㊍ ====================`
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

**Prefix : &**  

`copy` => `Makes a copy of the server where the command was made`
`emoteclone {id1} [id2]` => `Clone emojis from a server`
`[+]`  `&emoteclone (ID of the server where the emojis are) (ID Where you want the emotes to be cloned)`

`guildscrap` => `Scrap the pp and server banner`
`guildall` => `Allows you to leave the chosen servers`
`massmention` => `Mention 50 people from the server`
`connectvc {ID}` => `Connect to the channel indicated`
`leavevc` => `Leave to the channel indicated`

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1       ```'''
    await ctx.send(help_text)    

@bot.command()
async def account(ctx):
    await ctx.message.delete()
    help_text = '''>>> `=================== A C C O U N T ㊋ ====================`
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

**Prefix : &**

`dmallf {message}` => `Send the message to all your friends`
`leave_group` => `Leave all groups`
`anti_group {on/off}` => `Leaves instantly if you are invited to a group`

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1       ```'''
    await ctx.send(help_text)   

@bot.command()
async def utils(ctx):
    await ctx.message.delete()
    help_text = '''>>> `=================== U T I L S ㊈====================`
☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆

**Prefix : &**

`geoip {ip}` => `Locate IP`
`pingweb {url}` => `Ping Website`
`ping` => `Your ping`
`pp` => `Get the user's pp via their id`
`copyembed {ID}` => `Copy Embed`
`embed {webhook} [embed json code]` => `Create Embed`

☆, .- ~ * '¨¯¨' * · ~ -.¸--, .- ~ * '¨¯¨' * · ~ -.¸ ☆
```       C O R E - P R O J Ǝ C T | V1       ```'''
    await ctx.send(help_text)   

############################################################## G R O U P E ########################################################################

@bot.command()
async def leave_group(ctx):
  await ctx.message.delete()
  await ctx.send(
    f"Do you want to leave all group chats? React with ✅ for yes, or ❌ for no."
  )
  try:
    reaction, user = await bot.wait_for(
      'reaction_add',
      timeout=30.0,
      check=lambda reaction, user: user == ctx.author and str(reaction.emoji
                                                              ) in ['✅', '❌'])
  except asyncio.TimeoutError:
    await ctx.send("Timeout. Command canceled.")
    return
  if str(reaction.emoji) == '✅':
    try:
      for group in bot.private_channels:
        if isinstance(group, discord.GroupChannel):
          await group.leave()
          await ctx.send(f'Left group: {group.name}')
      await ctx.send('Left all groups.')
    except Exception as e:
      await ctx.send('An error occurred while leaving groups.')
      error_msg = traceback.format_exc()
      await send_error_log(error_msg)
      return
  else:
    await ctx.send("Command canceled.")


@bot.command()
async def anti_group(ctx, state):
  await ctx.message.delete()
  global anti_group_enabled
  if state.lower() == "on":
    anti_group_enabled = True
    await ctx.send("Anti-group mode is now enabled.")
  elif state.lower() == "off":
    anti_group_enabled = False
    await ctx.send("Anti-group mode is now disabled.")
  else:
    await ctx.send(
      "Invalid command. Use '!anti_group on' or '!anti_group off' to enable/disable anti-group mode."
    )
    return


@bot.event
async def on_private_channel_create(channel):
  global anti_group_enabled
  if isinstance(channel, discord.GroupChannel) and anti_group_enabled:
    await channel.leave()
    await channel.send(f"Sorry, I don't join group chats.")


@bot.event
async def on_error(event_method, *args, **kwargs):
  error_msg = traceback.format_exc()
  await send_error_log(error_msg)

############################################################## C L E A R S ########################################################################

@bot.command()
async def cleardm(ctx):
  await ctx.message.delete()
  await ctx.send(
    "Do you want to delete all direct messages? React with ✅ for yes, or ❌ for no."
  )
  try:
    reaction, user = await bot.wait_for(
      'reaction_add',
      timeout=30.0,
      check=lambda reaction, user: user == ctx.author and str(reaction.emoji
                                                              ) in ['✅', '❌'])
  except asyncio.TimeoutError:
    await ctx.send("Timeout. Command canceled.")
    return
  if str(reaction.emoji) == '✅':
    await ctx.send(
      "Deleting all direct messages in 5 seconds. This may take a while...")
    await asyncio.sleep(5)
    try:
      for channel in bot.private_channels:
        if isinstance(channel, discord.DMChannel):
          await ctx.send(f"Deleting messages in {channel}...")
          async for msg in channel.history(limit=None):
            if msg.author == bot.user:
              await msg.delete()
              await asyncio.sleep(random.randint(2, 5))
          await ctx.send(f"Finished deleting messages in {channel}.")
      await ctx.send("Done deleting all direct messages!")
    except Exception as e:
      error_msg = traceback.format_exc()
      await send_error_log(error_msg)
      await ctx.send(f"An error occurred while deleting DMs: {e}")
  else:
    await ctx.send("Command canceled.")
    
@bot.command()
async def clears(ctx):
  await ctx.message.delete()
  if ctx.guild is None:
    return await ctx.send("This command can only be executed on a server.")

  confirm_msg = await ctx.send(
    "Are you sure you want to delete all channels in this server? React with ✅ to confirm, otherwise react with ❌."
  )

  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

  try:
    reaction, _ = await bot.wait_for('reaction_add', timeout=60.0, check=check)
  except asyncio.TimeoutError:
    await confirm_msg.delete()
    return await ctx.send("Time elapsed. Canceling deletion of channels.")

  if str(reaction.emoji) == '❌':
    await confirm_msg.delete()
    return await ctx.send("Cancelled deletion of channels.")

  total_deleted = 0
  for channel in ctx.guild.channels:
    try:
      await channel.delete()
      total_deleted += 1
      delay = random.randint(1, 2)
      await asyncio.sleep(delay)

    except discord.errors.HTTPException:
      continue

  await ctx.guild.create_text_channel("core-self")
  
@bot.command()
async def clear_logs(ctx):
    try:
        img_dir = "logs/img"
        for file_name in os.listdir(img_dir):
            file_path = os.path.join(img_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"File {file_name} successfully deleted.")
            elif os.path.isdir(file_path):
                print(f"Folder {file_name} ignored.")

        url_file = "logs/url.txt"
        if os.path.isfile(url_file):
            with open(url_file, "w"):
                pass
            print("Contents of url.txt file deleted successfully.")
        else:
            print("File url.txt not found.")

        await ctx.send("Contents of 'img' folders and 'url.txt' file deleted successfully!")
    except Exception as e:
        print(f"Error encountered during command execution: {e}")
        await ctx.send("An error occurred while deleting the contents of the folders.")
  

############################################################## D M A L L F ########################################################################

@bot.command()
async def dmallf(ctx, *, message):
  await ctx.message.delete()
  if ctx.guild is not None:
    return await ctx.send("This command can only be executed in DMs.")

  confirm_msg = await ctx.send(
    f"Are you sure you want to send the message \"{message}\" to all your friends? React with ✅ to send, otherwise react with ❌."
  )

  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

  try:
    reaction, _ = await bot.wait_for('reaction_add', timeout=60.0, check=check)
  except asyncio.TimeoutError:
    await confirm_msg.delete()
    return await ctx.send("Time elapsed. Canceling sending to all friends.")

  if str(reaction.emoji) == '❌':
    await confirm_msg.delete()
    return await ctx.send("Cancelled sending to all friends.")

  total_sent = 0
  for friend in bot.user.friends:
    try:
      await friend.send(message)
      total_sent += 1
      delay = random.randint(5, 15)
      await asyncio.sleep(delay)

    except discord.errors.HTTPException:
      continue

  sent_msg = await ctx.send(
    f"The message \"{message}\" has been sent to \"{total_sent}\" friends.")

############################################################## T E R M I N A L ####################################################################

@bot.command()
async def geoip(ctx, *, ip):
    await ctx.message.delete() 
    response = requests.get(f"http://ip-api.com/json/{ip}")
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "success":
            response_message = f"**Country:** {data['country']}\n**Region:** {data['regionName']}\n**City:** {data['city']}\n**Latitude:** {data['lat']}\n**Longitude:** {data['lon']}\n**ZIP:** {data['zip']}"
        else:
            response_message = "Unable to geolocate IP address"
    else:
        response_message = "Unable to geolocate IP address"
    await ctx.send(response_message)
        
@bot.command()
async def pingweb(ctx, website=None):
    await ctx.message.delete()
    if website is None:
        await ctx.send(f'[ERROR]: Invalid input! Command: pingweb <website>')
        return
    try:
        r = requests.get(website).status_code
    except Exception as e:
        print(f"{Fore.RED}[ERROR]: {Fore.YELLOW}{e}" + Fore.RESET)
    if r == 404:
        await ctx.send(f'Website **down** *({r})*', delete_after=3)
    else:
        await ctx.send(f'Website **operational** *({r})*', delete_after=3)

@bot.command()
async def copyembed(ctx, message_id: int, skip_personal_emojis: bool = True):
    await ctx.message.delete()
    try:
        message = await ctx.channel.fetch_message(message_id)
        if message.embeds:
            for embed in message.embeds:
                embed_json = embed.to_dict()
                if skip_personal_emojis:
                    for field in embed_json.get('fields', []):
                        if 'emoji' in field:
                            field['emoji']['id'] = None
                await ctx.send(f"```json\n{json.dumps(embed_json, indent=4)}\n```")
        else:
            await ctx.send("This message does not contain an embed.")
    except Exception as e:
        await ctx.send(f"An error has occurred: {e}")






@bot.command()
async def embed(ctx, webhook_url: str, *, embed_json: str):
    await ctx.message.delete()
    embed_dict = json.loads(embed_json)
    payload = {
        "username": "Core",
        "avatar_url": "https://cdn.discordapp.com/attachments/1089172315645952033/1093364102350520340/Sans_titre.png",
        "embeds": [embed_dict]
    }

    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        await ctx.send("Embed sent successfully!")
    else:
        await ctx.send("Failed to send embed. Response code: " + str(response.status_code))
        

############################################################## G U I L D S ########################################################################

@bot.command()
async def guildall(ctx):
    await ctx.message.delete()
    if len(bot.guilds) == 0:
        return await ctx.send("This command can only be executed if the bot is in at least one server.")

    for guild in bot.guilds:
        confirm_msg = await ctx.send(f"Are you sure you want to leave {guild.name}? React with ✅ to confirm, ❌ to skip, or 1️⃣ to cancel.")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌', '1️⃣']

        try:
            reaction, _ = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.delete()
            await ctx.send(f"Timed out for {guild.name}")
            continue

        if str(reaction.emoji) == '1️⃣':
            await confirm_msg.delete()
            return await ctx.send("Cancelled deletion of servers.")

        if str(reaction.emoji) == '❌':
            await confirm_msg.delete()
            await ctx.send(f"Skipped {guild.name}")
            continue

        if str(reaction.emoji) == '✅':
            try:
                await guild.leave()
                await ctx.send(f"Successfully left {guild.name}")
            except Exception as e:
                await ctx.send(f"Failed to leave {guild.name}: {e}")

async def remove_all_recipients(channel):
    await asyncio.gather(*[channel.remove_recipient(r) for r in channel.recipients])

@bot.command()
async def copy(ctx):
    print(f'Guild copy command created by {ctx.author.name} ({ctx.author.id})')
    await ctx.message.delete()
    await bot.create_guild(f'backup-{ctx.guild.name}')
    print(f'New save guild created')
    await asyncio.sleep(4)
    for g in bot.guilds:
        if f'backup-{ctx.guild.name}' in g.name:
            print(f'Found the new save guild: {g.name} ({g.id})')
            for c in g.channels:
                await c.delete()
                print(f'Channel {c.name} ({c.id}) removed from new save guild')
            for role in reversed(ctx.guild.roles):
                if role.name != "@everyone":
                    perms = discord.Permissions.none()
                    for perm, value in role.permissions:
                        if value:
                            perms.update(**{perm: value})
                    new_role = await g.create_role(name=role.name, permissions=perms, colour=role.colour)
                    print(f'Role {new_role.name} ({new_role.id}) created in new save guild')
            for cate in ctx.guild.categories:
                x = await g.create_category(f"{cate.name}")
                await x.edit(position=cate.position)
                print(f'Category {x.name} ({x.id}) created in the new save guild')
                for chann in cate.channels:
                    if isinstance(chann, discord.VoiceChannel):
                        new_chan = await x.create_voice_channel(f"{chann}")
                        await new_chan.edit(position=chann.position, user_limit=chann.user_limit, bitrate=chann.bitrate, sync_permissions=True)
                        print(f'Voice Channel {chann.name} ({chann.id}) created in category {x.name} ({x.id}) from the new save guild')
                    if isinstance(chann, discord.TextChannel):
                        new_chan = await x.create_text_channel(f"{chann}")
                        await new_chan.edit(position=chann.position, topic=chann.topic, slowmode_delay=chann.slowmode_delay, sync_permissions=True)
                        perms = chann.overwrites
                        for role, perm in perms.items():
                            if isinstance(role, discord.Role):
                                new_role = discord.utils.get(g.roles, name=role.name)
                                if new_role is not None:
                                    await new_chan.set_permissions(new_role, overwrite=perm)
                        print(f'Text Channel {chann.name} ({chann.id}) created in category {x.name} ({x.id}) from the new save guild')
    try:
        icon = await ctx.guild.icon.read()
        await g.edit(icon=icon)
        print('New updated save guild icon')
    except Exception as e:
        await ctx.send(f'[ERROR]: {e}')
        print(f'An error occurred while updating the icon for the new save guild: {e}')
    print(f'Guild Copy Order Completed')

@bot.command()
async def massmention(ctx, *, message=None):
    await ctx.message.delete()
    members = ctx.guild.members
    if len(members) >= 50:
        sampling = random.sample(members, k=50)
    else:
        sampling = members
    post_message = "" if message is None else f"{message}\n\n"
    for user in sampling:
        post_message += user.mention
    await ctx.send(post_message)

@bot.command()
async def guildscrap(ctx):
    await ctx.message.delete()
    try:
        if not ctx.guild.icon:
            await ctx.send(f"**{ctx.guild.name}** has no icon")
        else:
            await ctx.send(f"Guild Icon : {ctx.guild.icon}")
        if not ctx.guild.banner_url:
            await ctx.send(f"**{ctx.guild.name}** has no banner")
        else:
            await ctx.send(f"Guild Banne : {ctx.guild.banner_url}")
    except Exception as e:
        print(f"[ERROR] An error occurred while executing the guildscrap command : {e}")
        await ctx.send(f"[ERROR] An error occurred while executing the guildscrap command : {e}")

@bot.command()
async def pp(ctx, user_id: int):
    await ctx.message.delete()
    try:
        user = await bot.fetch_user(user_id)
        if not user.avatar:
            await ctx.send(f"{user.name} has no profile picture")
        else:
            await ctx.send(f"{user.name}'s Profile Picture: {user.avatar}")
    except Exception as e:
        print(f"[ERROR] An error occurred while executing the userinfo command for user {user_id}: {e}")
        await ctx.send(f"[ERROR] An error occurred while executing the userinfo command for user {user_id}: {e}")


@bot.command()
async def emoteclone(ctx, source_id: int, target_id: int):
    print(f"cloneemojis command called between {source_id} and {target_id}")
    await ctx.message.delete()
    try:

        source_server = await bot.fetch_guild(source_id)
        emojis = await source_server.fetch_emojis()

        if len(emojis) > 50:
            emojis = emojis[:50]

        target_server = await bot.fetch_guild(target_id)
        for emoji in emojis:

            response = requests.get(str(emoji.url))
            if response.status_code != 200:
                print(f"Error while fetching image for emoji {emoji.name}")
                continue
            try:
                image = Image.open(BytesIO(response.content)).convert('RGBA')
                image_bytes = BytesIO()
                image.save(image_bytes, format='PNG')
                image_bytes.seek(0)

                await target_server.create_custom_emoji(name=emoji.name, image=image_bytes.read())
                print(f"Emoji {emoji.name} cloned successfully on the target server.")
            except IOError:
                print(f"Error while converting image for emoji {emoji.name}")
                continue

            await asyncio.sleep(3)

        await ctx.send("Emojis have been cloned successfully!")
    except Exception as e:
        print(f"Error encountered during command execution: {e}")
        await ctx.send("An error occurred while cloning emojis.")

@bot.command()
async def connectvc(ctx, channel_id: int):
    await ctx.message.delete()
    channel = bot.get_channel(channel_id)
    if channel and channel.type == discord.ChannelType.voice:
        try:
            await channel.connect()
            await ctx.send(f"Connected to voice channel: {channel.name}")
        except discord.errors.ClientException:
            await ctx.send("Already connected to a voice channel.")
    else:
        await ctx.send("Invalid voice channel ID.")

@bot.command()
async def leavevc(ctx):
    await ctx.message.delete()
    voice = ctx.guild.voice_client
    if voice:
        await voice.disconnect()
        await ctx.send("I logged out of the voice channel.")
    else:
        await ctx.send("I am not connected to a voice channel.")

############################################################## C O M M A N D S ####################################################################


############################################################## L O G I N ##########################################################################

bot.run(token)

############################################################## C O R E P R O J E C T ##############################################################
