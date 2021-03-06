from command import *

class C_Newgame(Command):
	name = "newgame"
	aliases = ["ng", "challenge", "atomic", "koth", "antichess", "crazyhouse", "horde", "racingkings"]
	helpstring = ["newgame <mention>", "Start a new game against someone!"]


	@classmethod
	async def run(self,ctx):
		if not ctx.game:
			if ctx.mentions:
				game2 = db.Game.from_user_id(ctx.mentions[0].id)

				if not game2:
					if ctx.mentions[0].id == ctx.mem.id:
						await ctx.ch.send("You can't connect with yourself in this way. Why not take a walk?")

					else:

						variant = VARIANT_STANDARD
						if ctx.command == "atomic": variant = VARIANT_ATOMIC
						elif ctx.command == "koth": variant = VARIANT_KOTH
						elif ctx.command == "antichess": variant = VARIANT_ANTICHESS
						elif ctx.command == "crazyhouse": variant = VARIANT_CRAZYHOUSE
						elif ctx.command == "horde": variant = VARIANT_HORDE
						elif ctx.command == "racingkings": variant = VARIANT_RACINGKINGS

						rated = variant == VARIANT_STANDARD
						if "casual" in ctx.args: rated = False

						m = await ctx.ch.send("{u1}, you are being challenged to a **{rated}** game of **{game}** by {u2}!".format(u1=ctx.mentions[0].mention,rated=RATED_NAMES[rated],game=VARIANT_NAMES[variant],u2=ctx.mem.mention))
						await m.add_reaction(ACCEPT_MARK)
						await m.add_reaction(DENY_MARK)
						try:

							def check(reaction, user):
								return user == ctx.mentions[0] and str(reaction) in [ACCEPT_MARK, DENY_MARK] and reaction.message.id == m.id
							reaction, user = await ctx.bot.wait_for('reaction_add', check=check, timeout=50)

							if str(reaction) == ACCEPT_MARK:
								await ctx.ch.trigger_typing()
								u1 = db.User.from_mem(ctx.mem)
								u2 = db.User.from_mem(ctx.mentions[0])
								if not db.Game.from_user_id(ctx.mem.id) and not db.Game.from_user_id(ctx.mentions[0].id):
									db.Game.new(u1.id, u2.id, variant=variant, rated=rated)

									if ctx.dbguild != None:
										ctx.dbguild.inc("games", 1)

									await ctx.ch.send('The game has started! Type {prefix}board to see the board!'.format(prefix=ctx.prefix))

									await ctx.bot.get_channel(config.LOGCHANNEL).send("`Create Game: "+str(u1.name)+" "+str(u2.name)+" "+str(ctx.guild.id)+"`")
									if config.MOTD == "":
										await ctx.bot.change_presence(activity=discord.Game(name=str(db.games.find().count())+" games!"),status=discord.Status.online)
									else:
										await ctx.bot.change_presence(activity=discord.Game(name=config.MOTD),status=discord.Status.online)
								else:
									await ctx.ch.send("{u1}, {u2} I dunno which, but one of you is already in a game!".format(u1=ctx.mem.mention,u2=ctx.mentions[0].mention))
							elif str(reaction) == DENY_MARK:
								await ctx.ch.send("{u1}, {u2} has declined the game request!".format(u1=ctx.mem.mention,u2=ctx.mentions[0].mention))
						except Exception as E:
							await ctx.ch.send("{u1}, the request has timed out!".format(u1=ctx.mem.mention))

				else:
					await ctx.ch.send('That user is currently in a game with another person!')
			else:
				await ctx.ch.send('You must mention another user!')
		else:
			await ctx.ch.send('You are already in a game! Resign it with {prefix}resign'.format(prefix=ctx.prefix))


command = C_Newgame
