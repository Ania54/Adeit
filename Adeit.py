import subprocess
import traceback
import discord
import aiohttp
import dotenv
import time
import sys
import os

support_server = 997825469376364565
emojimaster = 1315366598588108901
mama = 933471236175052871

bot = discord.Bot()

print(f"Pycord ver. {discord.__version__}")

@bot.event
async def on_ready():
	global emoji_dict
	global webhooks
	emoji_dict = await get_emojis(True)
	webhooks = await get_webhooks()
	print("Ready!")
	await status()

@bot.command()
async def very_test(ctx: discord.ApplicationContext):
	await ctx.respond("<a:Anime_Dance:1311727757843103825><a:busya:1311768022788345886>")
	await ctx.send(":Anime_Dance: :busya:")
	# be idle
	# await bot.change_presence(status=discord.Status.idle)

async def get_emojis(for_bot: bool = False):
	static, animated, app_emojis = [], [], []
	# differentiate animated emojis!!!!!!!!!!!
	all_emojis = {}

	if for_bot:
		for emoji in bot.get_guild(support_server).emojis:
			all_emojis[emoji.name] = (emoji.id, emoji.animated)
	else:
		for emoji in bot.get_guild(support_server).emojis:
			if emoji.animated == True:
				animated.append((emoji.name, emoji.id))
			else:
				static.append((emoji.name, emoji.id))
	
	async with aiohttp.ClientSession() as session:
		async with session.get(f"https://discord.com/api/v10/applications/{bot.user.id}/emojis", headers={"Authorization": f"Bot {bot.http.token}"}) as response:
			if response.status != 200:
				return all_emojis if for_bot else {"app_emojis": app_emojis, "static": static, "animated": animated}
			data = await response.json()
			if for_bot:
				for emoji in data.get("items", []):
					all_emojis[emoji["name"]] = (emoji["id"], emoji["animated"])
			else:
				for emoji in data.get("items", []):
					app_emojis.append((emoji["name"], emoji["id"], emoji["animated"]))

	return all_emojis if for_bot else {"app_emojis": app_emojis, "static": static, "animated": animated}

@bot.command()
async def lista_emoji(ctx: discord.ApplicationContext):
	all_emojis = await get_emojis()

	app_emojis = all_emojis["app_emojis"]
	static = all_emojis["static"]
	animated = all_emojis["animated"]

	message = f"# Emoji aplikacji ({len(app_emojis)}/2000):\n"
	for emoji in app_emojis:
		message += f"\n* <{'a' if emoji[2] else ''}:{emoji[0]}:{emoji[1]}>\t:{emoji[0]}: (ID: {emoji[1]}{', animowane' if emoji[2] else ''})"
	
	message += f"\n# Emoji z serwera ({len(static) + len(animated)}/100):\nStatyczne emoji ({len(static)}/50):"
	for emoji in static:
		message += f"\n* <:{emoji[0]}:{emoji[1]}>\t:{emoji[0]}: (ID: {emoji[1]})"
	message += f"\nAnimowane emoji ({len(animated)}/50):"
	for emoji in animated:
		message += f"\n* <a:{emoji[0]}:{emoji[1]}>\t:{emoji[0]}: (ID: {emoji[1]})"
	
	await ctx.respond(message)

@bot.command()
async def ping(ctx: discord.ApplicationContext):
	await ctx.respond(f"Pong :ping_pong:\n-# {round(bot.latency * 1000)} ms")

@bot.command()
async def restart(ctx: discord.ApplicationContext):
	if ctx.author.id != mama:
		await ctx.respond("Nie jesteś moją mamą :(")
		return
	await ctx.respond("Restartowanie…", ephemeral=True)
	python = sys.executable
	script = sys.argv[0]
	subprocess.Popen([python, script])
	sys.exit()

@bot.command()
async def wyłącz(ctx: discord.ApplicationContext):
	if ctx.author.id != mama:
		await ctx.respond("Nie jesteś moją mamą :(")
		return
	await ctx.respond("Wyłączanie…", ephemeral=True)
	await bot.change_presence(status = discord.Status.offline)
	await bot.close()

@bot.command()
async def błąd(ctx: discord.ApplicationContext):
	await ctx.respond(1/0) # Pozdrawiam wszystkich czytających

@bot.command()
async def nowe_emoji(ctx: discord.ApplicationContext):
	# if current guild is not support server
	if ctx.guild_id != support_server:
		await ctx.respond("Nowe emoji możesz dodać na moim serwerze wsparcia. Wysyłam zaproszenie (widoczne tylko dla Ciebie)")
		await ctx.respond("https://discord.com/invite/nbuvcv6n5s", ephemeral=True) # Send a message when the button is clicked
		return
	await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, id=emojimaster))
	await ctx.respond(f"Dodaj nowe emoji na tym serwerze (`Ustawienia serwera` > `Emoji` > `Przesyłanie emoji`)")

### @bot.command()
### async def m(ctx: discord.ApplicationContext, wiadomość: str):
### 	await ctx.respond("‌", delete_after=0, ephemeral=True)
### 	for emoji in emoji_dict:
### 		if f":{emoji}:" in wiadomość:
### 			wiadomość = wiadomość.replace(f":{emoji}:", f"<{"a" if emoji_dict[emoji][1] else ""}:{emoji}:{emoji_dict[emoji][0]}>")
### 	await ctx.send(wiadomość)

@bot.command()
async def m(ctx: discord.ApplicationContext, wiadomość: str):
	await ctx.respond("‌", delete_after=0, ephemeral=True)
	for emoji in emoji_dict:
		if f":{emoji}:" in wiadomość:
			wiadomość = wiadomość.replace(f":{emoji}:", f"<{"a" if emoji_dict[emoji][1] else ""}:{emoji}:{emoji_dict[emoji][0]}>")

	global webhooks
	if ctx.channel.id not in webhooks:
		await ctx.channel.create_webhook(name="Young Adeit")
		webhooks = await get_webhooks()
	webhook_url = webhooks[ctx.channel.id]

	async with aiohttp.ClientSession() as session:
		async with session.post(webhook_url, json={"content": wiadomość, "username": ctx.author.display_name, "avatar_url": ctx.author.avatar.url}) as response:
			if response.status != 204:
				await ctx.respond(f"Nie udało się wysłać wiadomości: {response.status} – {await response.text()}")

@bot.command()
async def odśwież_emoji(ctx: discord.ApplicationContext):
	start_time = time.time()
	emoji_dict = await get_emojis(True)
	end_time = time.time()
	# calculate the time difference
	await ctx.respond(f"Odświeżono emoji\n-# {round((end_time - start_time) * 1000)} ms")

async def get_webhooks():
	ret_webhooks = {}
	for guild in bot.guilds:
		webhooks = await guild.webhooks() # Fetch all webhooks for the guild
		for webhook in webhooks:
			if webhook.user == bot.user: # Check if the bot owns the webhook
				ret_webhooks[webhook.channel.id] = webhook.url
	return ret_webhooks

### @bot.command()
### async def send_webhook(ctx: discord.ApplicationContext):
### 	global webhooks
### 	if ctx.channel.id not in webhooks:
### 		await ctx.channel.create_webhook(name="Young Adeit")
### 		webhooks = await get_webhooks()
### 	webhook_url = webhooks[ctx.channel.id]
### 
### 	await ctx.respond(webhook_url)
### 
### 	async with aiohttp.ClientSession() as session:
### 		async with session.post(webhook_url, json={"content": "Hello, world!", "username": ctx.author.display_name}) as response:
### 			if response.status != 204:
### 				await ctx.respond(f"Nie udało się wysłać wiadomości: {response.status} – {await response.text()}")

### @bot.command()
### async def odśwież_webhooki(ctx: discord.ApplicationContext):
### 	pass

### @bot.command()
### async def nowy_webhook(ctx : discord.ApplicationContext, channel: discord.TextChannel = None):
### 	if ctx.author.id != mama:
### 		await ctx.respond("Nie jesteś moją mamą :(")
### 		return
### 	
### 	channel = channel or ctx.channel
### 	# Create a new webhook
### 	await channel.create_webhook(name="Young Adeit")
### 	await ctx.respond(f"Utworzono webhook na kanale {channel.mention}")

### @bot.command()
### async def usuń_webhooki(ctx: discord.ApplicationContext):
### 	if ctx.author.id != mama:
### 		await ctx.respond("Nie jesteś moją mamą :(")
### 		return
### 	
### 	count = 0
### 		
### 	for guild in bot.guilds:
### 		webhooks = await guild.webhooks() # Fetch all webhooks for the guild
### 		for webhook in webhooks:
### 			if webhook.user == bot.user: # Check if the bot owns the webhook
### 				await webhook.delete() # Delete the webhook
### 				count += 1
### 		
### 	if count == 0:
### 		await ctx.respond("Nie znaleziono żadnych webhooków")
### 	elif count == 1:
### 		await ctx.respond(f"Usunięto {count} webhook")
### 	elif (count >= 10 and int(str(count)[-2]) == 1) or (5 <= int(str(count)[-1]) <= 9 or int(str(count)[-1]) == 1):
### 		await ctx.respond(f"Usunięto {count} webhooków")
### 	else:
### 		await ctx.respond(f"Usunięto {count} webhooki")

### @bot.command()
### async def lista_webhooków(ctx: discord.ApplicationContext):
### 	if ctx.author.id != mama:
### 		await ctx.respond("Nie jesteś moją mamą :(")
### 		return
### 	
### 	message = ""
### 
### 	for guild in bot.guilds:
### 		webhooks = await guild.webhooks() # Fetch all webhooks for the guild
### 		for webhook in webhooks:
### 			if webhook.user == bot.user: # Check if the bot owns the webhook
### 				message += f"* {webhook.channel.mention} ({webhook.url})\n"
### 	if message == "":
### 		await ctx.respond("Nie znaleziono żadnych webhooków")
### 	else:
### 		await ctx.respond(message[:-1])

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
	if (str(error) == "Application Command raised an exception: HTTPException: 400 Bad Request (error code: 50035): Invalid Form Body\nIn content: Must be 2000 or fewer in length."):
		await ctx.respond(f"Wystąpił błąd: Osiągnięto limit znaków w wiadomości (2000). Zgłoś ten błąd mojej mamie: <@{mama}> (`@anilowa`)")
		return

	# Capture the full traceback as a string
	open("błąd.txt", "w").write("".join(traceback.format_exception(type(error), error, error.__traceback__)))

#	# Ensure the response is not too large for Discord's message limit (2000 characters)
#	if len(error_details) > 2000:
#		error_details = error_details[:1997] + '...'

	# Send the error details to Discord
	# await ctx.respond(f"```{error_details}```")  # Using `ephemeral=True` to make it visible only to the command user
	# attach file
	await ctx.respond(f"Wystąpił błąd: `{str(error)}` Zgłoś ten błąd mojej mamie: <@{mama}> (`@anilowa`)", file=discord.File("błąd.txt"))

async def status():
	print("updating status...")

	await bot.change_presence(status=discord.Status.streaming, activity=discord.Streaming(name=f"Działam na {len(bot.guilds)} serwerach!",
																					   url="https://youtube.com/watch?v=dQw4w9WgXcQ"))
	await bot.change_presence(status=discord.Status.streaming, activity=discord.Streaming(name=f"Nowy update: animowane emoji dla każdego! Sprawdź /help po więcej informacji",
																					   url="https://youtube.com/watch?v=dQw4w9WgXcQ"))

bot.run(open("token.txt").read())