import discord
from discord.ext import commands
from io import BytesIO
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import chess as Chess
from chess.svg import board as chess2svg

def eqor(val, *args):
	for arg in args:
		if val == arg:
			return True
	return False

''' BUGS:
undoing after checking the king in the first move leaves only one move
undoing after one move and a zugzwang leaves only one move
undoing doesn't work for movesMax = 1
'''
class chess(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.chessBoard = None
		self.movesMade = 0
		self.movesMax = 1
		self.player1 = None
		self.player2 = None
	
	def chess_clear(self):
		self.chessBoard = None
		self.movesMade = 0
		self.movesMax = 1
		self.player1 = None
		self.player2 = None
		print('Chess cleared')
	
	@commands.command()
	async def view(self, ctx):
		if self.chessBoard:
			# Generate and format board image
			img = BytesIO()
			svg = BytesIO(str(chess2svg(board=self.chessBoard, style='text{ fill: white; }')).encode())
			renderPM.drawToFile(svg2rlg(svg), img, fmt='PNG', bg=0x36393f)
			img.seek(0)
			# Old image rendering code
			'''
			from cairosvg import svg2png
			
			img = BytesIO()
			svg2png(bytestring=str(chess2svg(board=self.chessBoard, style='text{ fill: white; stroke: white; }')), write_to=img)
			img.seek(0)
			'''
			
			# Send board image to discord
			await ctx.send(file=discord.File(fp=img, filename='chessboard.png'))
	
	@commands.command()
	async def chess(self, ctx, member: discord.Member, type = 'normal'):
		if self.player1:
			await ctx.send('Chess is already in progress. Patience, young grasshopper.')
		elif member and member != ctx.author:
			self.movesMax = 2 if type == 'double' else 1
			self.player1 = ctx.author
			self.player2 = member
			await ctx.send('{} challenges {} to a game of chess! Use "/accept" to play or "/refuse" to run like a *coward*.'.format(
				self.player1.display_name, self.player2.display_name))
	
	@commands.command()
	async def refuse(self, ctx):
		if not self.chessBoard and self.player1 and eqor(ctx.author, self.player1, self.player2):
			await ctx.send('Chess cancled.')
			chess_clear(self)
	
	@commands.command()
	async def accept(self, ctx):
		# Board is uninitialized, player 2 is exists and command was called by player 2
		if not self.chessBoard and self.player2 and ctx.author == self.player2:
			print('Initializing chess...')
			# Tell players the game has started
			await ctx.send('Beginning chess with {} as white and {} as black. Maximum moves per turn is {}. Use "/move" to move a piece on your turn. Use "/view" to view the board or "/forfeit" to give up at any time. Use "/undo" to take back a move you just made.'.format(self.player1.display_name, self.player2.display_name, self.movesMax))
			
			# Initialize the chess board
			self.chessBoard = Chess.Board()
			
			# Show board
			await self.view(ctx)
			
			print('Chess is running')
	
	@commands.command()
	async def forfeit(self, ctx):
		if self.chessBoard and eqor(ctx.author, self.player1, self.player2):
			await ctx.send('Game over! {} forfeits!'.format(ctx.author.display_name))
			self.chess_clear()
	
	async def undo_aux(self, ctx):
		# Try to undo the move
		print('Attempting to undo move...')
		try:
			self.chessBoard.pop()
		except:
			print('Undo failed')
			await ctx.send('No moves to undo.')
			return
		print('Undo successful')
		
		# Show board
		await self.view(ctx)
		
		# Fix move count (turn switching is handled by pop)
		if self.movesMade > 0:
			self.movesMade -= 1
		else:
			self.movesMade = self.movesMax - 1
	
	@commands.command()
	async def undo(self, ctx):
		if self.chessBoard and eqor(ctx.author, self.player1, self.player2):
			# Make sure the caller was the last person to move
			if ctx.author == self.player1 if self.chessBoard.turn else self.player2:
				if self.movesMade != 0:
					await self.undo_aux(ctx)
				else:
					await ctx.send('That wasn\'t your move. Nice try.')
			elif self.movesMade == 0:
				await self.undo_aux(ctx)
			else:
				await ctx.send('That wasn\'t your move. Nice try.')
	
	async def chess_check_done(self, ctx, turn):
		if self.chessBoard.is_checkmate():
			await ctx.send('Game over! {} wins!'.format((self.player1 if turn else self.player2).display_name))
			self.chess_clear()
	
	async def move_aux(self, ctx, move: str, turn):
		color = 'White' if turn else 'Black'
		
		# Give current player the option to pass
		if move == 'zugzwang':
			print(color + ' passes')
			self.chessBoard.turn = not self.chessBoard.turn
			self.movesMade = 0
			await ctx.send('Turn skipped.')
		
		# The actual moves
		else:
			# Try move
			print('{} attempting move {}...'.format(color, move))
			try:
				self.chessBoard.push_san(move)
			except:
				print('Move failed')
				await ctx.send('That move is illegal.')
				return
			print('Move successful')
			
			# Show board
			await self.view(ctx)
			
			# Keep the color the same for two turns if no check
			self.movesMade += 1
			if self.movesMade < self.movesMax and not self.chessBoard.is_check():
				self.chessBoard.turn = turn
			else:
				# Turn is over, check if game is over
				await self.chess_check_done(ctx, turn)
				
				# Reset moves on turn switch
				self.movesMade = 0
	
	@commands.command()
	async def move(self, ctx, move: str):
		# Check if game is in progress and caller is one of the players
		if self.chessBoard and eqor(ctx.author, self.player1, self.player2):
			currentTurn = self.chessBoard.turn
			
			if currentTurn == Chess.WHITE:
				# Stop if it's not the caller's turn
				if ctx.author == self.player2:
					await ctx.send("It is currently {}'s turn.".format(self.player1.display_name))
					return
				
				# Try the move
				await self.move_aux(ctx, move, currentTurn)
			else:
				# Stop if it's not the caller's turn
				if ctx.author == self.player1:
					await ctx.send("It is currently {}'s turn.".format(self.player2.display_name))
					return
				
				# Try the move
				await self.move_aux(ctx, move, currentTurn)

def setup(bot):
	bot.add_cog(chess(bot))
