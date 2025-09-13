import discord
from discord.ext import commands
import random
import datetime
import feedparser
import os
from dotenv import load_dotenv

# ---------------------------
# Load Environment Variables
# ---------------------------
# This will load variables from a .env file if it exists (for local testing)
load_dotenv()

# Get the bot token from environment variables (Render will use this automatically)
YOUR_BOT_KEY = os.getenv("DISCORD_BOT_TOKEN")

if not YOUR_BOT_KEY:
    raise ValueError("Bot token not found! Set DISCORD_BOT_TOKEN in Render or .env file.")

# ---------------------------
# Bot Configuration
# ---------------------------
intents = discord.Intents.default()
intents.members = True  # Required for on_member_join
intents.message_content = True  # Required for commands

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ---------------------------
# Bot Events
# ---------------------------
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="The Internet Times 📡"))
    print(f'Logged in as {bot.user}!')
    print(f'Bot is now serving "{bot.guilds[0].name}"')
    print('------')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="👋ᴡᴇʟᴄᴏᴍᴇ")
    if not channel:
        print("Welcome channel '👋ᴡᴇʟᴄᴏᴍᴇ' not found.")
        return

    embed = discord.Embed(
        title=f"Welcome to {member.guild.name}!",
        description=f"Hola there, {member.mention}! Welcome to **The Internet Times** 📰✨\n\nWe're glad to have you here. Feel free to introduce yourself and check out the channels!",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text=f"Member #{member.guild.member_count} | Joined at")
    embed.timestamp = datetime.datetime.now()

    await channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You're missing some arguments for this command. 🤔")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the required permissions to run this command. 🚫")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"An unexpected error occurred: {error}")
        await ctx.send("An unexpected error occurred. Please try again later.")

# ---------------------------
# Commands (Help, Fun, Utility, Moderation)
# ---------------------------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="The Internet Times Bot Help",
        description="Here are all the available commands:",
        color=discord.Color.dark_purple()
    )

    embed.add_field(name="📰 General Commands", value="`!ping` - Checks the bot's latency.\n`!quote` - Get a random tech quote.\n`!technews` - Fetches the latest tech news.\n`!avatar [member]` - Shows a user's avatar.", inline=False)
    embed.add_field(name="💬 Fun Commands", value="`!hello` - Say hello in the lounge.\n`!poll \"Question\" \"Option1\" \"Option2\"...` - Creates a poll.", inline=False)
    embed.add_field(name="🛠️ Utility Commands", value="`!userinfo [member]` - Displays info about a user.\n`!serverinfo` - Displays info about the server.", inline=False)
    embed.add_field(name="👑 Moderation Commands", value="`!kick <member> [reason]` - Kicks a user.\n`!ban <member> [reason]` - Bans a user.\n`!unban <user_id>` - Unbans a user by their ID.\n`!clear <amount>` - Deletes a number of messages.", inline=False)

    embed.set_footer(text="Use !<command> to run a command. Example: !ping")
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! 🏓 Latency is {latency}ms.")

@bot.command()
async def quote(ctx):
    quotes = [
        "The Internet is becoming the town square for the global village. - Bill Gates",
        "Information is the oil of the 21st century, and analytics is the combustion engine. - Peter Sondergaard",
        "The Web as I envisaged it, we have not seen it yet. The future is still so much bigger than the past. - Tim Berners-Lee",
        "Technology is anything that wasn’t around when you were born. - Alan Kay",
        "The advance of technology is based on making it fit in so that you don't even notice it, so it's part of everyday life. - Bill Gates"
    ]
    await ctx.send(random.choice(quotes))

@bot.command()
async def hello(ctx):
    lounge_channels = ["🛋️ʟᴏᴜɴɢᴇ-1", "🛋️ʟᴏᴜɴɢᴇ-2", "🛋️ʟᴏᴜɴɢᴇ-3"]
    if ctx.channel.name in lounge_channels:
        await ctx.send(f"Hello {ctx.author.mention}! Welcome to the lounge 🛋️")
    else:
        await ctx.send("This command can only be used in the lounge channels!")

@bot.command()
async def technews(ctx):
    await ctx.send("Fetching the latest from the internet... 📰")
    try:
        feed = feedparser.parse("http://www.theverge.com/rss/index.xml")
        if not feed.entries:
            await ctx.send("Sorry, I couldn't fetch the news right now.")
            return

        latest_article = feed.entries[0]
        title = latest_article.title
        link = latest_article.link
        author = latest_article.author
        published_date = latest_article.published

        embed = discord.Embed(
            title=title,
            url=link,
            description=f"Published on {published_date}",
            color=discord.Color.orange()
        )
        embed.set_author(name=f"By {author} on The Verge")
        embed.set_footer(text="Stay informed!")

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send("An error occurred while fetching the news.")
        print(f"Error fetching news: {e}")

@bot.command()
async def poll(ctx, question: str, *options: str):
    if len(options) > 10:
        await ctx.send("You can only have a maximum of 10 options.")
        return
    if len(options) < 2:
        await ctx.send("You need at least 2 options to create a poll.")
        return

    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    description = [f"{reactions[i]} {option}" for i, option in enumerate(options)]

    embed = discord.Embed(
        title=question,
        description="\n".join(description),
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Poll created by {ctx.author.display_name}")

    poll_message = await ctx.send(embed=embed)
    for i in range(len(options)):
        await poll_message.add_reaction(reactions[i])

# ---------------------------
# Run the Bot
# ---------------------------
if __name__ == "__main__":
    bot.run(YOUR_BOT_KEY)
